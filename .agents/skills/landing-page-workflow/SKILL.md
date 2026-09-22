---
name: landing-page-workflow
description: Coordena intakes, cache, validação do manifest e construção de landing pages. Use para iniciar ou retomar o fluxo completo, operar somente com dados existentes ou aplicar refresh seletivo.
---

# Landing Page Workflow

Esta skill coordena; não duplica regras de coleta nem de construção. Leia [references/workflow.md](references/workflow.md) para modos e transições.

## Sequência

1. Gere um `entity_id` slug seguro a partir do nome, sem CPF/CNPJ. Inicialize com `python scripts/manifest.py init <entity_id> --display-name <nome>` ou consulte o manifest existente.
2. Execute `python scripts/workflow.py plan <entity_id>` com os flags solicitados. O plano considera TTL de 24 horas para Instagram e 7 dias para web.
3. Quando indicado, use `$instagram-profile-intake` e aguarde seu patch; depois use `$web-profile-intake`. Os intakes são sequenciais para que o segundo possa desambiguar com links já confirmados. Respostas do usuário são persistidas pela skill proprietária.
4. Se houve coleta, encerre a rodada e planeje novamente. Nunca chame o builder no mesmo plano que contém intake.
5. Atualize `intake_status.media` como `ready` somente quando a avaliação de mídia terminar; isso não autoriza reutilização, registrada por ativo. Valide o manifest e use `$landing-page-builder` apenas quando `builder_ready` for `true`.
6. Respeite `--existing-only`: não colete nem atualize fontes; encaminhe ao builder apenas se os dados existentes forem suficientes e válidos.

Use `--refresh` para invalidar ambos os caches, `--refresh-instagram` ou `--refresh-web` para apenas um. Atualize somente `workflow.*` e `intake_status.media`; inclusive respostas do usuário nas demais seções pertencem às skills proprietárias.
