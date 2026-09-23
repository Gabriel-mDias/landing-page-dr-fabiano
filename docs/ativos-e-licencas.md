# Ativos visuais, fontes e autorizações

Inventário revisado em 23/09/2026. O responsável do projeto declarou que todos os ativos locais e pessoas retratadas foram autorizados para edição e publicação comercial. Originais ficam em `media/`; somente derivações otimizadas estão em `public/assets/`.

| Origem | Derivação publicada | Uso | Autorização/observação |
|---|---|---|---|
| `media/Logo/logo.png` | `public/assets/logo/logo-full.png`, `logo-icon.png` | Marca, header, rodapé e favicon | PNG oficial fornecido e autorizado; monograma apenas recortado, sem alteração do desenho |
| `media/Hero/hero_procedimento_1.mp4` | `hero-procedimento.mp4`, `.webm`, `hero-poster-1200.*` | Hero desktop e fallback | Recorte de 10 s, sem áudio; quadros amostrados sem identificação visível |
| `media/Profissional/fabiano_1.png` | `fabiano-retrato-*` | Apresentação sobre fundo editorial em CSS | Retrato transparente autorizado do profissional |
| `media/Profissional/fabiano_2.png` | `fabiano-cirurgia-*` | Poster de vídeo | Retrato autorizado do profissional |
| `media/Profissional/fabiano_3.png` | `fabiano-perfil-*` | Trajetória/poster | Retrato autorizado do profissional |
| `media/Espaço/espaco_1.png` e `espaco_3.png` | `adriele-*` | Equipe/recepção | Adriele Marques; uso comercial autorizado |
| `media/Espaço/espaco_2.png` | `consultorio-recepcao-*` | Consultório | Espaço real autorizado |
| `media/Instagram/post_2/movimento_e_saude.mp4` | `movimento-saude.mp4` | Cirurgia sob demanda | A partir de 5 s; sem áudio; autorizado |
| `media/Instagram/post_3/outras_abordagens_alem_da_cirurgia.mp4` | `infiltracoes.mp4`, `.vtt` | Infiltrações sob demanda | Áudio mantido; legenda e transcrição resumidas a partir do conteúdo aprovado |
| `media/Instagram/ia_generated_1/tratamento_fisioterapeutico_1.jpg` | `fisioterapia-conceitual-*` | Ambientação conceitual | Gerada por IA; identificada; não representa paciente, caso ou resultado |

As imagens responsivas possuem AVIF e WebP em larguras de até 1280 px (1600 px na imagem conceitual), adequadas a telas de alta densidade. O processamento usa redimensionamento Lanczos, nitidez leve e compressão de alta qualidade, sem reconstrução generativa; originais permanecem intactos em `media/`. O pipeline reprodutível está em `scripts/process-images.py`. Nenhum quadro publicado deve conter prontuário, nome de paciente ou dado identificável; a verificação deve ser repetida antes de qualquer publicação definitiva.

## Fontes

| Família | Arquivo | Origem | Licença |
|---|---|---|---|
| Libre Bodoni Variable | `public/assets/fonts/LibreBodoni-Variable.ttf` | Repositório oficial Google Fonts | SIL Open Font License 1.1; cópia em `OFL-Libre-Bodoni.txt` |
| Montserrat Variable | `public/assets/fonts/Montserrat-Variable.ttf` | Repositório oficial Google Fonts | SIL Open Font License 1.1; cópia em `OFL-Montserrat.txt` |

## Limites

Os ativos não devem ser reutilizados fora deste projeto sem nova verificação de autorização. Não há banco de imagens apresentado como paciente, equipe ou endosso, nem imagem de caso/resultado clínico.
