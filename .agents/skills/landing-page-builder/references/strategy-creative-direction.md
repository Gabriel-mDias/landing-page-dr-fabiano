# Estratégia e direção criativa

## Classificação

Escolha um arquétipo primário. Use um secundário apenas quando houver duas naturezas reais no negócio; ele complementa seções, nunca a hero nem a conversão acima da dobra.

| Arquétipo | Narrativa dominante | Provas principais | Tipos de CTA primário |
|---|---|---|---|
| `serviço` | problema → confiança → método → acompanhamento | equipe, processo, depoimentos, credenciais | `agendar`, `diagnosticar`, `conversar` |
| `produto` | desejo → demonstração → diferenciais → redução de risco | fotos, especificações, avaliações, garantia, entrega | `comprar`, `reservar`, `pedir_orçamento` |
| `profissional` | autoridade → trajetória → adequação | portfólio, experiência, resultados, reconhecimento | `contratar`, `solicitar_proposta` |
| `institucional` | posicionamento → capacidade → reputação | história, liderança, operação, números confirmados | `conhecer_soluções`, `falar_com_empresa` |

Registre no frontmatter os valores exatos da tabela em `modelo_narrativo`, `foco_de_prova` e `tipo_cta_primário`. O mapa de seções pode variar, mas deve concretizar essa lógica.

## Decisão da hero

- `estática`: padrão sem vídeo próprio de qualidade, quando copy/produto exige foco ou performance é prioritária.
- `vídeo`: somente quando movimento demonstra ambiente, processo, experiência ou produto.
- `híbrida`: vídeo no desktop e poster no mobile, em conexão reduzida e com `prefers-reduced-motion`.

Vídeo ou híbrida exige autorização, poster, MP4/WebM quando viável, sem áudio, `muted`, `playsinline`, duração curta, overlay contrastante, fallback de erro e até 6 MB por padrão. Se algo faltar, registre a razão e selecione `estática`; não deixe a implementação decidir.

A composição registra frase de impacto, explicação da oferta, prova/qualificador imediato, CTA primário, CTA secundário não concorrente quando útil, mídia, justificativa, legibilidade, enquadramento e comportamento responsivo.

## Documento obrigatório

Crie `requisitos/direcao-criativa.md` a partir do modelo do repositório e mantenha o frontmatter sincronizado com o conteúdo humano. Inclua:

- uma leitura visual em uma frase e os controles de variância, movimento e densidade, justificados pelo público, marca, referências e restrições;
- arquétipos, objetivo e hierarquia de conversão;
- narrativa e mapa de seções;
- modalidade/composição da hero;
- paleta por papel semântico e contraste;
- famílias, pesos, fallback, arquivos e licença tipográfica;
- banco de slogans/frases com origem e recomendação central;
- referências aprovadas/rejeitadas, assets e restrições;
- itens confirmados, inferidos, pendentes e suas autorizações.

Use [visual-taste.md](visual-taste.md) como revisão de composição e acabamento. Seus controles orientam decisões dentro da direção aprovada; não substituem arquétipo, evidência, autorização nem os sete itens do gate.

## Gate de aprovação

Antes de editar HTML, CSS, JS visual ou mídia, obtenha aprovação explícita para `arquétipo`, `hero`, `paleta`, `tipografia`, `frase_central`, `seções` e `cta`. Registre responsável e data. Todos devem estar `aprovado`; silêncio, pesquisa, implementação preexistente ou aprovação parcial não contam.

Execute `npm run validate:publication` antes de publicar. Itens inferidos sem aprovação, licenças indefinidas, divergência entre briefing/direção, CTA concorrente acima da dobra e vídeo incompleto são bloqueadores.
