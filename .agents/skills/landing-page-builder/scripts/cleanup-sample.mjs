import { access, mkdir, readFile, rename } from 'node:fs/promises';
import { basename, dirname, resolve, relative, sep } from 'node:path';

const sampleFiles = [
  'public/assets/logo/aurora-symbol.svg',
  'public/assets/images/hero-clinica.webp',
  'public/assets/images/consulta.webp',
  'public/assets/images/consultorio.webp',
  'public/assets/images/acolhimento.webp',
  'public/favicon.svg'
];

function valueAfter(flag) {
  const index = process.argv.indexOf(flag);
  return index >= 0 ? process.argv[index + 1] : undefined;
}

const projectName = valueAfter('--confirm');
const root = resolve(valueAfter('--root') || process.cwd());
const dryRun = process.argv.includes('--dry-run');

if (!projectName || /^(sample|demo|exemplo)$/i.test(projectName)) {
  throw new Error('Informe o novo projeto com --confirm "Nome do projeto"; nomes genéricos não são aceitos.');
}

for (const marker of ['package.json', '.agents/skills/landing-page-builder/SKILL.md']) {
  await access(resolve(root, marker)).catch(() => {
    throw new Error(`Raiz recusada: marcador ausente (${marker}). Execute na raiz do projeto clonado.`);
  });
}

const packageJson = JSON.parse(await readFile(resolve(root, 'package.json'), 'utf8'));
if (packageJson.name !== 'landing-page-sample') {
  throw new Error(`Limpeza recusada: package.json não identifica o template landing-page-sample (${packageJson.name}).`);
}

const safeName = projectName.normalize('NFKD').replace(/[^a-zA-Z0-9_-]+/g, '-').replace(/^-|-$/g, '').toLowerCase();
if (!safeName) throw new Error('O nome confirmado não produz um identificador de backup seguro.');
const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
const backupRoot = resolve(root, '.sample-backup', `${safeName}-${timestamp}`);
const found = [];

for (const file of sampleFiles) {
  const source = resolve(root, file);
  if (!source.startsWith(`${root}${sep}`)) throw new Error(`Caminho fora da raiz recusado: ${file}`);
  try {
    await access(source);
    found.push({ file, source, destination: resolve(backupRoot, file) });
  } catch {
    // Reexecução segura: ativos já movidos não são erro.
  }
}

if (!found.length) {
  console.log('Nenhum ativo demonstrativo conhecido encontrado; nada a limpar.');
  process.exit(0);
}

console.log(`${dryRun ? 'Simulação' : 'Limpeza'} do sample para “${projectName}”:`);
for (const item of found) console.log(`- ${relative(root, item.source)} -> ${relative(root, item.destination)}`);

if (!dryRun) {
  for (const item of found) {
    await mkdir(dirname(item.destination), { recursive: true });
    await rename(item.source, item.destination);
  }
  console.log(`Backup recuperável criado em ${relative(root, backupRoot)}.`);
  console.log('Substitua marca, favicon e imagens antes de executar npm test.');
}
