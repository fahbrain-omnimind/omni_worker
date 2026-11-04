# vendor/ — dependências vendored (autossuficiência do omni_worker)

English: Third-party/sibling-repo code vendored so `omni_worker` does not
depend on other repositories at build or runtime.

pt-BR: Código de terceiros/repos irmãos vendored para o `omni_worker` não
depender de outros repositórios em build ou runtime.

## kernel/ — crates Rust `omnimind_*`

- **Proveniência**: `omni_node/src/kernel/{kernel_compute,metrics,freud10d}`
  (upstream público: `devomnimind/Doxihewu-OmniMind-Kernel`), copiado verbatim
  em 2026-11-04.
- **Licença**: `CC-BY-NC-ND-4.0` (campo `license` de cada `Cargo.toml`) —
  **excluída do grant Apache-2.0** que cobre o restante deste repositório.
  Uso local não-comercial; não redistribuir derivados.
- **Build**: `bash scripts/build_kernel.sh` (cargo >= 1.85, headers Python).
  Produz `libomnimind_<crate>.so` instalado como `omnimind_<crate>` no
  site-packages do interpretador ativo. Opcional: `kernel_hooks` degrada
  para fallback Python quando ausente.

## src/omni_coworker/vendor/dunker_architecture.py

- **Proveniência**: `omni_node/src/cognitive/dunker_architecture.py`,
  copiado verbatim em 2026-11-04 (stdlib puro: `logging` + `typing`).
- Consumido por `omni_coworker.agency.dunker` (prioridade sobre os
  fallbacks legados `OMNI_NODE_ROOT`/PYTHONPATH).
