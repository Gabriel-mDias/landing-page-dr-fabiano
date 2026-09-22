# Critérios de qualidade e entrega

## Estratégia e autorização

- `npm run validate:publication` confirma briefing e direção coerentes.
- Arquétipo muda narrativa, provas, seções e tipo de CTA conforme a referência estratégica.
- Secundário não disputa hero nem CTA acima da dobra.
- Cor, fonte, frase e ativo têm fonte, data, contexto, estado e autorização/licença.
- Toda inferência utilizada e as sete decisões criativas estão aprovadas.
- Vídeo incompleto resulta em direção `estática`; vídeo/híbrida implementado cumpre poster, silêncio, atributos, fallback, contraste, redução de movimento e orçamento.

## Conteúdo e função

- Nome, nicho, local, contato, promessa, prova e CTA batem com o briefing.
- Não restam dados/ativos do template apresentados como reais.
- Pessoas, credenciais, depoimentos e métricas têm fonte e aprovação.
- Menu, âncoras, coleções, FAQ e formulário funcionam por mouse e teclado.
- Links apontam para destinos confirmados; formulário sem chave cai para WhatsApp e comunica estado com `aria-live`.

## Visual e responsivo

Execute o smoke test em 390, 768 e 1440 px. Verifique overflow, cortes, distorções, hero, foco, contraste, imagens, console, redução de movimento e navegação mobile. Imagens abaixo da dobra têm dimensões e lazy loading.

Execute também o preflight de [visual-taste.md](visual-taste.md): compare a implementação com a leitura visual e os três controles aprovados; verifique variedade de composição, repetição de padrões, consistência de CTA, cor, formas, tipografia e tema; remova movimento sem função e clichês sem justificativa. Registre exceções deliberadas na direção criativa.

## SEO, segurança e operação

H1 único, title/description/canonical/OG coerentes; `noindex` permanece em demo ou enquanto o gate falhar. Nenhum segredo ou dado desnecessário é versionado. Workflows usam permissões mínimas e lockfile.

## Evidência

Informe comandos/resultados, arquivos centrais, preview, modalidade de hero, integrações desativadas, pendências e próximo passo. Não declare autorização ou integração externa funcional sem evidência.
