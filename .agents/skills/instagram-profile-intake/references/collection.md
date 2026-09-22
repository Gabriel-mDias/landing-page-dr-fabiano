# Coleta pública do Instagram

Prefira API oficial ou material acessível sem autenticação. Colete biografia, categoria, links, avatar e uma amostra pequena de posts materialmente úteis. Não implemente scraper privado, bypass ou coleta irrestrita.

`instagram/instagram.json` deve manter URL de origem, instante de consulta e fatos extraídos. Cada item de mídia deve indicar arquivo relativo, URL de origem, tipo, data, legenda resumida e autorização (`unknown`, `allowed` ou `denied`). Use separadores `/` nos caminhos.

O índice de candidatos deve conter somente os melhores itens por função provável (`logo`, `hero`, `portrait`, `gallery` ou `unknown`), com score e motivos determinísticos. Não duplique os binários em `candidates/`.
