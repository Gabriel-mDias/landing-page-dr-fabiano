# Consumo seletivo da descoberta

## Fonte canônica

Comece por `.assets/<entity_id>/manifest.json`. Use `python scripts/manifest.py get <entity_id> <caminho>` para ler seções pontuais e abra apenas os arquivos que elas referenciam. O builder não pesquisa a web, não coleta Instagram e não varre diretórios de posts, raws ou avaliações.

Considere `intake_status.instagram`, `intake_status.web`, `cache.*.expires_at` e `conflicts[]`. Se um dado material estiver ausente, `stale`, `failed` ou em conflito não resolvido, pare a etapa dependente e retorne ao `$landing-page-workflow` com uma descrição curta da lacuna.

## Seleção mínima

Leia primeiro identidade, oferta, contatos, proveniência e índices de candidatos. Abra uma mídia apenas quando ela for candidata real para uma seção. Para cada cor, fonte, frase, logo, grafismo, foto, vídeo, campanha, prova e dado escolhido, preserve no briefing:

| Valor | Fonte/URL/arquivo | Consultado em | Contexto original | Estado | Licença/autorização e escopo |
|---|---|---|---|---|---|

Separe descoberta de autorização. Uma publicação oficial prova origem, mas não necessariamente permite copiar o ativo. Para fontes, anote família, pesos, arquivos, licença e fallback. Para cores, anote código, origem, função e cores proibidas. Para frases, anote se deve permanecer literal, ser adaptada ou apenas inspirar a mensagem.

Colete público, dores, objeções, promessa verificável, provas disponíveis, conversão principal, tom, formalidade, palavras preferidas/proibidas e referências aprovadas/rejeitadas. Registre vínculo, credencial e autorização de cada pessoa.

## Lacunas adaptativas

O workflow decide se atualiza o intake ou pergunta ao usuário. O builder pode formular perguntas como:

- “Quais cores representam a marca hoje? Há alguma cor que não deve ser usada?”
- “Existe uma fonte oficial ou algum estilo tipográfico que o cliente deseja preservar?”
- “Qual frase, bordão ou ideia o empreendedor já usa e considera reconhecível?”
- “Essa frase deve permanecer literal, ser adaptada ou apenas inspirar a nova mensagem?”
- “Quais sites ou marcas representam a aparência desejada? O que deve ser evitado?”
- “Qual ação única o visitante deve realizar após compreender a página?”

Também pergunte quando houver conflito de identidade, claim regulado, contato principal ausente, integração paga ou autorização indefinida de pessoa/ativo. Avance com inferências reversíveis somente até a proposta de direção criativa.

## Prova e conversão

Para cada oferta, registre problema, benefício, escopo e limite. Depoimento exige texto aprovado, autoria ou anonimização, autorização e data. Métrica exige evidência. Confirme o destino real do CTA, WhatsApp E.164, mensagem, e-mail, formulário e fallback antes de publicar.
