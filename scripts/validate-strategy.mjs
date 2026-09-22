import { readFile, readdir } from 'node:fs/promises';
import { resolve, join } from 'node:path';

const root = resolve(import.meta.dirname, '..');
const archetypes = {
  'serviço': {
    narrative: 'problema > confiança > método > acompanhamento',
    proof: 'equipe, processo, depoimentos, credenciais',
    ctas: ['agendar', 'diagnosticar', 'conversar']
  },
  produto: {
    narrative: 'desejo > demonstração > diferenciais > redução de risco',
    proof: 'fotos, especificações, avaliações, garantia, entrega',
    ctas: ['comprar', 'reservar', 'pedir_orçamento']
  },
  profissional: {
    narrative: 'autoridade > trajetória > adequação',
    proof: 'portfólio, experiência, resultados, reconhecimento',
    ctas: ['contratar', 'solicitar_proposta']
  },
  institucional: {
    narrative: 'posicionamento > capacidade > reputação',
    proof: 'história, liderança, operação, números confirmados',
    ctas: ['conhecer_soluções', 'falar_com_empresa']
  }
};

function scalar(raw) {
  const value = raw.trim().replace(/^['"]|['"]$/g, '');
  if (value === 'true') return true;
  if (value === 'false') return false;
  if (/^-?\d+(\.\d+)?$/.test(value)) return Number(value);
  return value;
}

export function parseFrontmatter(content, file = 'documento') {
  const match = content.match(/^---\s*\r?\n([\s\S]*?)\r?\n---/);
  if (!match) throw new Error(`${file}: frontmatter YAML ausente.`);
  const data = {};
  for (const line of match[1].split(/\r?\n/)) {
    if (!line.trim() || line.trimStart().startsWith('#')) continue;
    const separator = line.indexOf(':');
    if (separator < 1) throw new Error(`${file}: linha inválida no frontmatter: ${line}`);
    data[line.slice(0, separator).trim()] = scalar(line.slice(separator + 1));
  }
  return data;
}

function missing(value) {
  return value === undefined || value === '' || /^(PREENCHER|placeholder|pendente|indefinida)$/i.test(String(value));
}

function validDate(value) {
  return /^\d{4}-\d{2}-\d{2}$/.test(String(value));
}

function authorized(value) {
  return ['aprovado', 'autorizado', 'licenciado', 'não_aplicável'].includes(value);
}

function validateSourceGroup(data, prefix, errors, { license = false } = {}) {
  for (const suffix of ['estado', 'fonte', 'consultado_em', 'contexto', 'autorização']) {
    if (missing(data[`${prefix}_${suffix}`])) errors.push(`${prefix}_${suffix} está ausente ou pendente.`);
  }
  if (!validDate(data[`${prefix}_consultado_em`])) errors.push(`${prefix}_consultado_em deve usar AAAA-MM-DD.`);
  if (!['confirmado', 'inferido'].includes(data[`${prefix}_estado`])) {
    errors.push(`${prefix}_estado deve estar confirmado ou inferido para publicação.`);
  }
  if (!authorized(data[`${prefix}_autorização`])) errors.push(`${prefix}_autorização não permite reutilização.`);
  if (data[`${prefix}_estado`] === 'inferido' && data[`${prefix}_autorização`] !== 'aprovado') {
    errors.push(`${prefix} inferido exige autorização explicitamente aprovada.`);
  }
  if (license && missing(data[`${prefix}_licença`])) errors.push(`${prefix}_licença está ausente ou indefinida.`);
}

export function validatePair(briefing, direction) {
  const errors = [];
  if (briefing.tipo_documento !== 'briefing') errors.push('O primeiro documento não é um briefing.');
  if (direction.tipo_documento !== 'direção_criativa') errors.push('O segundo documento não é uma direção criativa.');

  for (const key of ['nome_cliente', 'arquétipo_primário', 'arquétipo_secundário', 'objetivo_de_conversão', 'cta_primário', 'tipo_cta_primário']) {
    if (missing(briefing[key])) errors.push(`Briefing: ${key} está ausente.`);
    if (missing(direction[key])) errors.push(`Direção: ${key} está ausente.`);
    if (!missing(briefing[key]) && briefing[key] !== direction[key]) errors.push(`${key} diverge entre briefing e direção.`);
  }

  const primary = archetypes[direction.arquétipo_primário];
  if (!primary) errors.push('arquétipo_primário deve ser serviço, produto, profissional ou institucional.');
  if (direction.arquétipo_secundário !== 'não_aplicável') {
    if (!archetypes[direction.arquétipo_secundário]) errors.push('arquétipo_secundário é inválido.');
    if (direction.arquétipo_secundário === direction.arquétipo_primário) errors.push('Arquétipos primário e secundário não podem ser iguais.');
  }
  if (primary) {
    if (direction.modelo_narrativo !== primary.narrative) errors.push('modelo_narrativo não corresponde ao arquétipo primário.');
    if (direction.foco_de_prova !== primary.proof) errors.push('foco_de_prova não corresponde ao arquétipo primário.');
    if (!primary.ctas.includes(direction.tipo_cta_primário)) errors.push('tipo_cta_primário não corresponde ao arquétipo primário.');
  }
  if (direction.cta_acima_da_dobra_quantidade !== 1) errors.push('Deve existir exatamente um CTA primário acima da dobra.');
  if (direction.cta_secundário_compete !== false) errors.push('O CTA secundário não pode competir com a conversão primária.');

  if (!['estática', 'vídeo', 'híbrida'].includes(direction.hero_modalidade)) errors.push('hero_modalidade é inválida.');
  if (direction.hero_modalidade === 'estática' && ['vídeo', 'híbrida'].includes(direction.hero_solicitada) && missing(direction.hero_fallback_motivo)) {
    errors.push('Hero solicitada em vídeo/híbrida que virou estática precisa de motivo de fallback.');
  }
  if (['vídeo', 'híbrida'].includes(direction.hero_modalidade)) {
    if (!authorized(direction.hero_autorização)) errors.push('Vídeo da hero não está autorizado.');
    if (missing(direction.hero_poster)) errors.push('Vídeo da hero exige poster.');
    for (const key of ['hero_sem_áudio', 'hero_muted', 'hero_playsinline', 'hero_duração_curta', 'hero_overlay_contraste', 'hero_fallback_erro', 'hero_redução_movimento']) {
      if (direction[key] !== true) errors.push(`${key} deve ser true para hero com vídeo.`);
    }
    if (!(direction.hero_tamanho_mb > 0 && direction.hero_tamanho_mb <= 6)) errors.push('hero_tamanho_mb deve ser maior que zero e no máximo 6.');
    if (direction.hero_modalidade === 'híbrida' && direction.hero_mobile_estático !== true) errors.push('Hero híbrida exige poster estático no mobile.');
  }

  for (const prefix of ['paleta', 'frase_central']) validateSourceGroup(direction, prefix, errors);
  validateSourceGroup(direction, 'tipografia', errors, { license: true });
  validateSourceGroup(briefing, 'nome_cliente', errors);
  validateSourceGroup(briefing, 'conversão', errors);
  if (!['confirmado', 'não_aplicável'].includes(briefing.contato_principal_estado)) errors.push('contato_principal_estado bloqueia publicação.');
  if (briefing.seo_estado !== 'confirmado') errors.push('seo_estado deve estar confirmado.');

  for (const item of ['arquétipo', 'hero', 'paleta', 'tipografia', 'frase_central', 'seções', 'cta']) {
    if (direction[`aprovação_${item}`] !== 'aprovado') errors.push(`aprovação_${item} está pendente.`);
  }
  if (missing(direction.aprovado_por)) errors.push('aprovado_por está ausente.');
  if (!validDate(direction.aprovado_em)) errors.push('aprovado_em deve usar AAAA-MM-DD.');
  return errors;
}

async function loadPair(briefingPath, directionPath) {
  const briefingText = await readFile(briefingPath, 'utf8');
  const directionText = await readFile(directionPath, 'utf8');
  return {
    briefing: parseFrontmatter(briefingText, briefingPath),
    direction: parseFrontmatter(directionText, directionPath)
  };
}

function requireFailure(name, briefing, direction, expected) {
  const errors = validatePair(briefing, direction);
  if (!errors.some((error) => error.includes(expected))) throw new Error(`${name}: cenário negativo não foi recusado por “${expected}”.`);
}

async function dryRuns() {
  const fixturesRoot = resolve(root, 'tests/skill-dry-run/cases');
  const names = (await readdir(fixturesRoot, { withFileTypes: true })).filter((entry) => entry.isDirectory()).map((entry) => entry.name).sort();
  if (names.length !== 5) throw new Error(`Esperados 5 dry runs, encontrados ${names.length}.`);
  const primarySeen = new Set();
  const heroSeen = new Set();

  for (const name of names) {
    const { briefing, direction } = await loadPair(join(fixturesRoot, name, 'briefing.md'), join(fixturesRoot, name, 'direcao-criativa.md'));
    const errors = validatePair(briefing, direction);
    if (errors.length) throw new Error(`${name}:\n- ${errors.join('\n- ')}`);
    primarySeen.add(direction.arquétipo_primário);
    heroSeen.add(`${direction.hero_solicitada}->${direction.hero_modalidade}`);
    console.log(`dry run ${name}: ${direction.arquétipo_primário}, hero ${direction.hero_solicitada} → ${direction.hero_modalidade}, aprovado`);

    if (name === '01-servico-estatica') {
      requireFailure('inferência sem aprovação', briefing, { ...direction, paleta_estado: 'inferido', paleta_autorização: 'pendente' }, 'paleta_autorização');
      requireFailure('licença tipográfica indefinida', briefing, { ...direction, tipografia_licença: 'indefinida' }, 'tipografia_licença');
      requireFailure('CTA concorrente', briefing, { ...direction, cta_secundário_compete: true }, 'não pode competir');
    }
    if (name === '02-produto-video') {
      requireFailure('vídeo sem poster', briefing, { ...direction, hero_poster: 'PREENCHER' }, 'exige poster');
    }
  }
  if (primarySeen.size !== 4) throw new Error('Os dry runs não cobrem os quatro arquétipos primários.');
  for (const expected of ['estática->estática', 'vídeo->vídeo', 'vídeo->estática', 'híbrida->híbrida']) {
    if (!heroSeen.has(expected)) throw new Error(`Cobertura de hero ausente: ${expected}.`);
  }
  console.log('Dry runs: 4 arquétipos, caso híbrido, fallbacks e cenários negativos confirmados.');
}

async function main() {
  const args = process.argv.slice(2);
  if (args.includes('--dry-runs')) return dryRuns();
  const briefingIndex = args.indexOf('--briefing');
  const directionIndex = args.indexOf('--direction');
  const briefingPath = resolve(root, briefingIndex >= 0 ? args[briefingIndex + 1] : 'requisitos/briefing.md');
  const directionPath = resolve(root, directionIndex >= 0 ? args[directionIndex + 1] : 'requisitos/direcao-criativa.md');
  let pair;
  try {
    pair = await loadPair(briefingPath, directionPath);
  } catch (error) {
    if (error.code === 'ENOENT') {
      console.error(`Publicação recusada: artefato obrigatório ausente (${error.path}).`);
      process.exit(1);
    }
    throw error;
  }
  const { briefing, direction } = pair;
  const errors = validatePair(briefing, direction);
  if (errors.length) {
    console.error(`Publicação recusada:\n- ${errors.join('\n- ')}`);
    process.exit(1);
  }
  console.log('Gate de estratégia e direção criativa aprovado para publicação.');
}

await main();
