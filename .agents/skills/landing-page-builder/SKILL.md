---
name: landing-page-builder
description: Constrói e valida uma landing page a partir de um manifest de entidade já coletado, cobrindo briefing, direção criativa, aprovação, implementação, SEO e publicação. Use ao criar, personalizar, migrar ou revisar a página; não use para coletar Instagram ou pesquisar a web.
---

# Landing Page Builder

Transforme este repositório-base em uma página publicável para um cliente real. Preserve a arquitetura reutilizável e trate pesquisa, aprovação criativa e implementação como fases distintas.

## Compatibilidade mínima

Este é o arquivo canônico para **Codex, Gemini e Claude**. `AGENTS.md`, `GEMINI.md` e `CLAUDE.md` apenas apontam para ele. Use Markdown, caminhos relativos e critérios observáveis; não crie versões divergentes.

## Sequência obrigatória

1. **Ler o projeto.** Leia `README.md`, `docs/`, `src/config/site.js`, `index.html`, workflows e o estado do Git. Preserve alterações do usuário.
2. **Consumir a descoberta.** Leia [references/discovery.md](references/discovery.md), obtenha `.assets/<entity_id>/manifest.json` e selecione somente os campos e arquivos necessários à etapa atual. Não percorra raws, posts, imagens ou avaliações em massa. Se dados essenciais estiverem ausentes, vencidos ou conflitantes, devolva ao `$landing-page-workflow` uma descrição curta para que ele registre `workflow.last_error`; não colete Instagram ou web diretamente.
3. **Confirmar o novo projeto e limpar a demo.** Somente ao converter uma cópia nova deste template para um cliente confirmado, execute o script do sistema atual a partir da raiz: no PowerShell, `& '.\.agents\skills\landing-page-builder\scripts\cleanup-sample.bat' --confirm 'Nome do projeto'`; no Prompt de Comando, `call .agents\skills\landing-page-builder\scripts\cleanup-sample.bat --confirm "Nome do projeto"`; em Linux/macOS, `sh .agents/skills/landing-page-builder/scripts/cleanup-sample.sh --confirm "Nome do projeto"`. Para inspecionar sem mover arquivos, acrescente `--dry-run`. Não execute ao revisar uma página já adaptada ou este repositório-base. O script move apenas ativos demonstrativos enumerados para `.sample-backup/`, preservando recuperação; não amplie a lista sem conferir cada caminho.
4. **Classificar e criar o briefing.** Copie `requisitos/briefing-template.md` para `requisitos/briefing.md`. Defina `arquétipo_primário` e, para negócio híbrido, no máximo um `arquétipo_secundário`. Confirme uma conversão e um CTA primários.
5. **Propor a direção criativa.** Leia [references/strategy-creative-direction.md](references/strategy-creative-direction.md) e aplique a revisão compatível de [references/visual-taste.md](references/visual-taste.md). Copie `requisitos/direcao-criativa-template.md` para `requisitos/direcao-criativa.md` e complete leitura visual, controles de variância/movimento/densidade, narrativa, mapa de seções, hero, paleta, tipografia, repertório verbal, referências, assets e restrições. Marque toda proposta nova como `inferido`.
6. **Obter aprovação.** Não altere a implementação visual enquanto arquétipo, hero, paleta, tipografia, frase central, seções e CTA não estiverem individualmente `aprovado` no frontmatter da direção criativa. Pesquisa ou briefing não equivalem a autorização.
7. **Implementar.** Após a aprovação, leia [references/implementation.md](references/implementation.md). A hero e a ordem narrativa obedecem ao arquétipo primário; o secundário só acrescenta seções e não cria CTA concorrente acima da dobra.
8. **Validar.** Leia [references/quality-gates.md](references/quality-gates.md) e refaça o preflight de [references/visual-taste.md](references/visual-taste.md). Execute `npm test`, `npm run validate:publication` e o smoke test em 390, 768 e 1440 px. Um gate de publicação recusado é bloqueador, não um aviso.
9. **Entregar.** Liste arquivos, comandos, decisões aprovadas, integrações desativadas e pendências. Não faça push nem ative domínio, analytics, formulário ou serviço externo sem autorização.

## Estados e origem

Use `confirmado`, `inferido`, `placeholder` ou `não_aplicável`. Um item `inferido` só pode entrar na página após aprovação explícita; aprovação muda a autorização de uso, não transforma a fonte em oficial. Preserve frase histórica literalmente somente se for curta, atribuível ao cliente e autorizada. Identifique adaptações como propostas editoriais.

Precedência de conflitos: (1) usuário; (2) site oficial; (3) Instagram oficial; (4) Maps/Google Business; (5) LinkedIn; (6) terceiros. Preserve o conflito no manifest em vez de sobrescrevê-lo silenciosamente.

## Limite de escrita

Esta skill pode alterar somente `landing_page.*` no manifest, sempre por `python scripts/manifest.py patch <entity_id> landing_page <patch.json>`. Briefing, direção criativa e arquivos da página continuam sendo suas saídas normais, mas seções de intake, cache, contatos e workflow pertencem às skills proprietárias.

## Invariantes

- Nunca invente dados legais, pessoas, credenciais, clientes, números, prêmios, depoimentos ou resultados.
- Evidência pública não autoriza reutilização de logo, foto, vídeo, fonte, grafismo ou frase. Registre escopo e responsável pela autorização.
- Fonte da marca tem prioridade. Sem fonte oficial, use família OFL auto-hospedada ou fonte de sistema; não adicione CDN de fontes por padrão.
- Hero de vídeo exige mídia própria autorizada, poster, silêncio, `muted`, `playsinline`, duração curta, overlay legível, fallback de erro, redução de movimento e orçamento padrão de até 6 MB. Sem todos os requisitos, use hero estática.
- Pessoas de banco de imagens nunca representam cliente, paciente, equipe ou endosso.
- Em áreas reguladas, claims e credenciais precisam de aprovação; prefira linguagem descritiva.
- Nunca exponha segredos. Use WhatsApp E.164 e encode a mensagem.
- Preserve HTML semântico, teclado, foco visível, labels, alt contextual e `prefers-reduced-motion`.
- Não publique com placeholder em identidade, contato, conversão, SEO, licença/autorização ou aprovação criativa.

## Saídas mínimas

- `requisitos/briefing.md` com frontmatter validável e inventário de fontes;
- `requisitos/direcao-criativa.md` aprovado antes do código;
- página responsiva, `src/config/site.js`, ativos/licenças e SEO coerentes;
- `npm test`, gate de publicação e smoke test documentados;
- handoff com pendências explícitas.
