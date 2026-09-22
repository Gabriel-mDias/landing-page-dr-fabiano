---
name: web-profile-intake
description: Pesquisa informações profissionais e comerciais públicas para o manifest de uma entidade, com proveniência e conflitos. Use para intake web; não construa páginas nem investigue dados pessoais.
---

# Web Profile Intake

Pesquise somente informações profissionais ou comerciais relevantes e grave `.assets/<entity_id>/web/web-profile.json`, `web/sources.json` e apenas raws realmente úteis. Leia [references/research.md](references/research.md) quando houver desambiguação, avaliações ou conflito.

## Fluxo

1. Consulte manifest, cache e fontes existentes. Reutilize cache válido salvo refresh.
2. Confirme a entidade com ao menos dois sinais coerentes. CPF/CNPJ integral pode ser usado transitoriamente para desambiguação, mas nunca persistido em arquivo, manifest, patch ou log.
3. Priorize usuário, site oficial, Instagram oficial, Maps/Google Business, LinkedIn e terceiros, nessa ordem. Registre valores divergentes em `conflicts[]`; não sobrescreva silenciosamente.
4. Mantenha URL, título, plataforma, data de consulta e fatos sustentados por cada fonte. Avaliações ficam separadas por plataforma, usando apenas estatísticas públicas ou amostras limitadas.
5. Aplique patch com owner `web`. Não edite implementação da landing page.

## Ownership

Escreva somente `web.*`, `contact.*`, `timestamps.web_collected_at`, `intake_status.web`, `cache.web` e `conflicts`. Minimize dados pessoais, não faça doxxing e não armazene documentos integrais. Respostas do usuário sobre fontes, contatos e resolução de conflitos são persistidas por esta skill; o workflow não altera esses campos.
