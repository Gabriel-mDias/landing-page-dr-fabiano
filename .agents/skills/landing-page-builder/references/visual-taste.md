# Revisão de gosto visual

Esta referência adapta ao workflow os critérios compatíveis da [Taste Skill](https://github.com/leonxlnx/taste-skill), fixados no commit `e79ca9ec7e071eb3a3b623c4fb752e853fc3ed58` e distribuídos sob licença MIT. Consulte [docs/third-party-notices.md](../../../../docs/third-party-notices.md). A fonte externa está em v2 experimental; por isso este projeto mantém uma adaptação pequena, revisável e independente da stack.

Ela atua dentro do `landing-page-builder`. Não é um novo intake, não escreve no manifest e não substitui briefing, direção criativa, aprovação, licenças ou gates de publicação. Em conflito, prevalecem os dados confirmados da marca, as autorizações, a acessibilidade, a arquitetura existente e as regras do builder.

## Leitura e controles

Antes da proposta, registre uma frase no formato: “Página [tipo] para [público], com linguagem [atributos], orientada por [família estética ou sistema]”. Baseie a leitura no briefing, referências, ativos da marca, mercado e restrições. Não invente uma estética por hábito.

Defina e justifique três controles de 1 a 10:

- **Variância de composição:** de simétrica e previsível a assimétrica e experimental.
- **Intensidade de movimento:** de estados estáticos a coreografia orientada por rolagem.
- **Densidade visual:** de espaçosa a concentrada.

Os números não são metas isoladas. Eles tornam a intenção verificável e devem respeitar público e contexto. Áreas reguladas, serviços públicos e experiências críticas tendem a menor variância e movimento. Composições assimétricas devem colapsar explicitamente para uma coluna abaixo de 768 px.

## Critérios compatíveis

- Preserve marca, conteúdo e stack. Não instale React, Tailwind, Motion, design systems, bibliotecas de ícones ou fontes porque aparecem na fonte externa. Verifique `package.json` antes de qualquer dependência e justifique a inclusão.
- Evite padrões automáticos: gradiente roxo sem vínculo com a marca, hero centralizada por reflexo, três cards idênticos, excesso de vidro, etiquetas em caixa alta sobre toda seção, listas em cartões sem hierarquia e tipografia escolhida apenas por tendência.
- Use uma família de layout por função. Uma página longa precisa de ritmo; não repita a mesma grade ou alternância imagem/texto em sequência sem motivo. Cards, elevação e divisores devem comunicar agrupamento real.
- Mantenha uma regra coerente para raio, sombras, acento, neutros e tema. Mudanças de tema entre seções exigem intenção registrada. Cores e fontes confirmadas pela marca sempre têm prioridade.
- A hero deve comunicar oferta, prova ou qualificador e CTA sem esconder a ação inicial. Dimensione texto e mídia juntos e confira 390, 768 e 1440 px. Limites editoriais são guias; a clareza do conteúdo aprovado prevalece.
- Use um rótulo consistente para a mesma intenção de CTA. CTAs não quebram linha no desktop e mantêm contraste, foco, estado ativo e destino confirmado.
- Movimento precisa comunicar hierarquia, narrativa, feedback ou mudança de estado. Anime preferencialmente `transform` e `opacity`, respeite `prefers-reduced-motion` e remova efeitos que não tenham uma função explicável.
- Imagens e provas visuais precisam ser reais, autorizadas e relevantes. Não fabrique logos, clientes, screenshots, avatares, métricas ou depoimentos. Placeholders permanecem identificados e bloqueiam publicação quando forem materiais.
- Formulários mantêm labels visíveis, erros contextuais, foco perceptível e contraste WCAG AA. Placeholder não substitui label.
- Leia todo o texto visível antes da entrega. Remova linguagem genérica, quebras gramaticais, dados fictícios e inconsistências entre títulos, CTA, alt text e mensagens de estado.

## Preflight

Antes de pedir aprovação da direção e novamente antes da entrega, responda:

1. A implementação corresponde à leitura visual e aos três controles registrados?
2. Marca, conteúdo, licenças, autorização e acessibilidade prevaleceram sobre preferências estéticas?
3. Hero, navegação e CTA funcionam sem corte, quebra indevida ou ação escondida nos três viewports?
4. Há repetição de layouts, cards, etiquetas ou efeitos que torne a página genérica?
5. Cor, formas, sombras, tipografia, tema e rótulos de CTA seguem regras consistentes?
6. Cada animação tem função, bom desempenho e alternativa com movimento reduzido?
7. Imagens, logos, provas e números têm origem e autorização, sem simulação apresentada como fato?
8. As exceções deliberadas estão registradas na direção criativa com justificativa?

Falhas materiais voltam para a direção criativa ou implementação. Uma preferência da fonte externa que contrarie o briefing não é falha; registre a decisão e siga o projeto.
