import { readFile, access } from 'node:fs/promises';
import { resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..');
const required = [
  'index.html', 'src/config/site.js', 'src/js/main.js', 'src/styles/main.css',
  'public/robots.txt', 'public/site.webmanifest', 'public/404.html',
  '.github/workflows/quality.yml', '.github/workflows/deploy.yml',
  '.agents/skills/landing-page-builder/SKILL.md',
  '.agents/skills/landing-page-builder/references/strategy-creative-direction.md',
  '.agents/skills/landing-page-builder/references/visual-taste.md',
  'docs/third-party-notices.md',
  '.agents/skills/landing-page-builder/scripts/cleanup-sample.bat',
  '.agents/skills/landing-page-builder/scripts/cleanup-sample.sh',
  '.agents/skills/landing-page-builder/scripts/cleanup-sample.mjs',
  '.agents/skills/instagram-profile-intake/SKILL.md', '.agents/skills/web-profile-intake/SKILL.md',
  '.agents/skills/landing-page-workflow/SKILL.md', '.agents/skills/landing-page-workflow/references/workflow.md',
  'contracts/manifest.template.json', 'contracts/manifest.schema.json',
  'scripts/manifest.py', 'scripts/asset_utils.py', 'scripts/workflow.py', 'tests/test_manifest.py',
  'requisitos/briefing-template.md', 'requisitos/direcao-criativa-template.md',
  'scripts/validate-strategy.mjs', 'CLAUDE.md', 'GEMINI.md', 'AGENTS.md'
];
const failures = [];
for (const file of required) {
  try { await access(resolve(root, file)); }
  catch { failures.push(`Arquivo obrigatório ausente: ${file}`); }
}

const html = await readFile(resolve(root, 'index.html'), 'utf8');
const config = await readFile(resolve(root, 'src/config/site.js'), 'utf8');
const skill = await readFile(resolve(root, '.agents/skills/landing-page-builder/SKILL.md'), 'utf8').catch(() => '');
const manifestSchema = await readFile(resolve(root, 'contracts/manifest.schema.json'), 'utf8').catch(() => '');
const gitignore = await readFile(resolve(root, '.gitignore'), 'utf8').catch(() => '');
const packageJson = JSON.parse(await readFile(resolve(root, 'package.json'), 'utf8'));

for (const hook of ['data-contact="whatsapp"', 'data-contact-form', 'aria-live="polite"']) if (!html.includes(hook)) failures.push(`Hook genérico ausente: ${hook}`);
for (const field of ['whatsapp:', 'email:', 'instagramUrl:', 'accessKey:']) if (!config.includes(field)) failures.push(`Configuração genérica ausente: ${field}`);

// Marca, mídia e narrativa da Clínica Aurora só são obrigatórias no sample intacto.
if (packageJson.name === 'landing-page-sample') {
  for (const file of ['public/favicon.svg', 'public/assets/logo/aurora-symbol.svg', 'public/assets/images/hero-clinica.webp', 'public/assets/images/consulta.webp', 'public/assets/images/consultorio.webp', 'public/assets/images/acolhimento.webp']) {
    try { await access(resolve(root, file)); } catch { failures.push(`Fixture exclusiva do sample ausente: ${file}`); }
  }
  for (const section of ['inicio', 'sobre', 'especialidades', 'jornada', 'duvidas', 'contato']) if (!html.includes(`id="${section}"`)) failures.push(`Seção da demo Aurora ausente: #${section}`);
}

if (!skill.includes('Claude') || !skill.includes('Gemini') || !skill.includes('Codex')) failures.push('A skill não declara compatibilidade com Codex, Gemini e Claude.');
if (!skill.includes('landing_page.*') || !skill.includes('$landing-page-workflow')) failures.push('O builder não documenta ownership e retorno ao workflow.');
if (!skill.includes('references/visual-taste.md')) failures.push('O builder não integra o preflight de gosto visual.');
if (!manifestSchema.includes('https://json-schema.org/draft/2020-12/schema') || !manifestSchema.includes('"const": "1.0"')) failures.push('O contrato não declara JSON Schema 2020-12 e schema_version 1.0.');
const ignored = gitignore.split(/\r?\n/);
if (!ignored.includes('.assets/')) failures.push('.assets/ não está no .gitignore.');
if (!ignored.includes('__pycache__/') || !ignored.includes('*.pyc')) failures.push('Caches Python não estão ignorados.');
if (failures.length) { console.error(failures.map((item) => `- ${item}`).join('\n')); process.exit(1); }
console.log(`Validação concluída: ${required.length} arquivos e invariantes genéricos confirmados.`);
