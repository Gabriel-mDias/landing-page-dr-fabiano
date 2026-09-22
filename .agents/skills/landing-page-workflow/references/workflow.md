# Fluxo coordenado

```text
init/consultar manifest
  -> planejar cache
  -> Instagram (se necessário)
  -> web (se necessário)
  -> replanejar em nova rodada
  -> validar manifest
  -> builder
```

## Modos

- Padrão: reutiliza cache válido e agenda somente intake ausente, vencido, parcial ou falho.
- `--refresh`: agenda os dois intakes independentemente do TTL.
- `--refresh-instagram` / `--refresh-web`: ignora apenas o cache escolhido.
- `--existing-only`: nunca agenda intake; reporta lacunas e permite builder somente quando ambos os domínios estão `ready` e não vencidos.

Qualquer plano com coleta termina em `replan` e nunca inclui `run_builder`. Conflito material aberto, intake diferente de `ready`, cache vencido ou avaliação de mídia incompleta bloqueia o builder. `intake_status.media = ready` significa apenas avaliação concluída, não licença de uso. Lacunas e respostas são gravadas pela skill proprietária; o workflow escreve somente `workflow.*` e `intake_status.media`.
