-- Projeto LTD

-- Fluxo Git (GitFlow)

Este projeto utiliza o GitFlow como estratégia de versionamento e organização do código.

-- Branches principais (definitivas)

master → contém o código estável, pronto para produção.

develop → contém o código em desenvolvimento (base para novas funcionalidades).

-- Branches de suporte (temporárias)

São criadas quando necessário e removidas após o merge:

feature/<nome-da-funcionalidade>

Usada para desenvolver novas funcionalidades.

Exemplo: feature/login-usuario

release/<versao>

Usada para estabilizar uma nova versão antes de ir para produção.

Exemplo: release/1.0.0

hotfix/<ajuste>

Usada para corrigir problemas críticos em produção.

Exemplo: hotfix/corrigir-bug-tal

-- Branches modelo já criadas neste repositório

Foram criadas apenas para ilustrar o fluxo:

feature/exemplo

release/0.1.0

hotfix/exemplo

⚠️ Atenção: essas branches são apenas demonstrativas e podem ser apagadas quando o time estiver confortável com o fluxo.

-- Regras básicas para contribuição

Nunca faça commits diretamente em master ou develop.

Crie uma branch a partir de develop para cada nova funcionalidade (feature/...).

Faça Pull Requests para integrar suas mudanças de volta.

Sempre descreva claramente no PR:

O que foi feito.

Qual problema resolve.

Qual branch deve receber o merge.

Mantenha sua branch atualizada com develop antes de abrir o PR.

-- Convenções

Nomes de branches sempre em kebab-case (exemplo: feature/cadastro-usuario).

Commits devem ser claros e descritivos (ex.: feat: adiciona tela de cadastro).
Nomes de branches sempre em kebab-case (exemplo: feature/cadastro-usuario).

Commits devem ser claros e descritivos (ex.: feat: adiciona tela de cadastro).
