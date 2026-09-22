# Implementação após aprovação

Só prossiga se `requisitos/direcao-criativa.md` tiver as sete aprovações exigidas. Se a direção mudar, atualize o documento e obtenha nova aprovação antes do código.

Antes de implementar, releia o preflight de [visual-taste.md](visual-taste.md). Preserve a stack existente e traduza os critérios para HTML, CSS e JavaScript nativos; nenhuma biblioteca indicada pela referência é dependência automática.

| Necessidade | Arquivo principal |
|---|---|
| marca, contatos, mapa e formulário | `src/config/site.js` |
| SEO, estrutura e conteúdo | `index.html` |
| paleta, tipografia e espaçamento | `src/styles/tokens.css` |
| componentes e seções | `src/styles/components.css`, `src/styles/sections.css` |
| contato e interações | `src/js/modules/` |
| mídia e logo | `public/assets/` |
| licenças | `docs/ativos-e-licencas.md` |

## Tradução da estratégia

A hero, a promessa e a sequência da página seguem o arquétipo primário. O secundário pode adicionar prova ou seção abaixo da dobra, sem CTA rival. Remova blocos que não tenham conteúdo confiável.

Implemente a composição de hero aprovada: impacto, oferta, prova imediata, CTA e mídia. Para vídeo, inclua poster e fallback estático, `autoplay muted loop playsinline`, ausência de áudio útil, overlay e comportamento para erro, mobile, conexão reduzida e `prefers-reduced-motion`. Não carregue vídeo quando o modo aprovado for estático.

Use fontes fornecidas/licenciadas ou OFL auto-hospedadas/fontes de sistema. Não adicione CDN por padrão. Converta paleta aprovada em tokens sem alterar papéis semânticos e verifique contraste.

## Conteúdo, integração e publicação

Mantenha H1 único, títulos hierárquicos, CTA descritivo, alt contextual e imagens decorativas vazias. Não coloque texto essencial em imagens.

Centralize integrações em `SITE_CONFIG`. Nunca exponha segredo. Analytics e pixels entram somente após decisão explícita. Substitua `noindex` apenas depois do gate de publicação. Defina title, description, canonical, OG e dados estruturados com dados confirmados.

Confira `git status`; não sobrescreva trabalho do usuário nem copie contatos, chaves, depoimentos ou ativos de outro cliente.
