---
name: instagram-profile-intake
description: Coleta dados e mídias publicamente acessíveis de um perfil oficial do Instagram para o manifest de uma entidade. Use para intake ou atualização do Instagram; não construa páginas nem contorne autenticação.
---

# Instagram Profile Intake

Colete somente o necessário para preencher `.assets/<entity_id>/instagram/` e atualizar o domínio `instagram` do manifest. Leia [references/collection.md](references/collection.md) antes da coleta.

## Fluxo

1. Leia `instagram.handle`, `instagram.url`, o cache e os conflitos pelo `scripts/manifest.py`.
2. Se o cache estiver válido e não houver refresh, reutilize-o.
3. Confirme que o perfil é público e oficial por links cruzados ou identificadores coerentes. Não una homônimos.
4. Grave metadados em `instagram/instagram.json`, mídia de perfil em `instagram/profile/`, posts selecionados em `instagram/posts/` e o índice JSON em `instagram/candidates/`.
5. Execute `scripts/asset_utils.py inventory` para hash, formato, dimensões, transparência, nome, proporção e classificação heurística. Inspeção visual por IA é permitida apenas na pequena lista de candidatos.
6. Aplique patch com owner `instagram`. Sem acesso público confiável ou credencial adequada, registre `partial`; não burle login, rate limit ou controles de acesso.

## Ownership

Escreva somente `instagram.*`, `timestamps.instagram_collected_at`, `intake_status.instagram` e `cache.instagram`. O status agregado `intake_status.media` pertence ao workflow. Não construa ou edite a landing page.

Dados públicos não implicam licença de reuso. Preserve URL, data de consulta, contexto e estado de autorização. Nunca registre cookies, tokens ou credenciais. Respostas do usuário sobre perfil, fonte ou autorização são persistidas por esta skill em sua seção proprietária; o workflow não as grava.
