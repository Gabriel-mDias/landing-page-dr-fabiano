# Matriz de dry runs da skill

Os pares `briefing.md` + `direcao-criativa.md` em `cases/` representam decisões completas e aprovadas:

| Caso | Primário | Secundário | Hero solicitada → escolhida | Risco coberto |
|---|---|---|---|---|
| `01-servico-estatica` | serviço | — | estática → estática | ausência de vídeo e foco em performance |
| `02-produto-video` | produto | — | vídeo → vídeo | vídeo próprio com poster, atributos e orçamento |
| `03-profissional-video-sem-poster` | profissional | — | vídeo → estática | poster ausente força fallback |
| `04-institucional-sem-video` | institucional | — | estática → estática | capacidade/reputação sem mídia em movimento |
| `05-hibrido-reduced-motion` | serviço | institucional | híbrida → híbrida | secundário sem CTA rival e poster no mobile/reduced motion |

O runner também deriva casos negativos em memória e exige recusa de publicação para inferência sem aprovação, licença tipográfica indefinida, vídeo sem poster e CTA concorrente acima da dobra.
