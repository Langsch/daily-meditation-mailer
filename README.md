# daily-meditation-mailer

Pega a meditação diária publicada em [opusdei.org/pt-br/meditation](https://opusdei.org/pt-br/meditation/) e manda por email, formatada em HTML.

Roda todo dia às 06:00 (horário de Brasília) sem depender de nenhuma máquina ligada: o GitHub Actions faz o trabalho e quem aperta o botão é um cron externo. Também dá pra rodar na mão, local.

## Rodar local

```
pip install -r requirements.txt
cp .env.example .env   # preenche as variáveis
export $(cat .env | xargs)
python main.py             # busca a meditação de hoje e envia
python main.py --dry-run   # só gera meditation_preview.html, não envia nada
```

## Configurar o envio (Gmail)

1. Ative a verificação em duas etapas na conta Google que vai enviar os emails.
2. Crie uma "senha de app" em https://myaccount.google.com/apppasswords (escolha qualquer nome, ex. "meditation-mailer").
3. Use essa senha de 16 letras como `GMAIL_APP_PASSWORD`. Não é a senha normal da conta.

## Rodar todo dia via GitHub Actions

Em Settings → Secrets and variables → Actions do repo, cria estes secrets:

- `GMAIL_USER`: o email que envia
- `GMAIL_APP_PASSWORD`: a senha de app gerada acima
- `RECIPIENTS`: lista de destinatários separados por vírgula (fica privado, não aparece pra quem olha o repo)

Pra disparar na mão: aba Actions → Send daily meditation → Run workflow.

## Por que o agendamento é externo

O `daily.yml` não tem `schedule:`. Tinha, e não funcionava. O cron do GitHub Actions em repo gratuito é best-effort e cai numa fila de baixa prioridade: as runs de 12, 13 e 14/09/2026 estavam marcadas pras 09:00 UTC e rodaram 12:29, 13:30 e 15:23. O atraso só piorava.

A saída foi tirar o gatilho de lá. Um cron no [cron-job.org](https://cron-job.org) chama a API de `workflow_dispatch` no horário certo, e dispatch não entra nessa fila.

### Configurar

Primeiro um token, em Settings → Developer settings → Personal access tokens → Fine-grained tokens:

- acesso só ao repo `daily-meditation-mailer`
- uma permissão só: Repository permissions → Actions → Read and write
- anota a data de expiração em algum lugar. Token vencido derruba o envio calado.

Depois um job novo no cron-job.org:

- URL: `https://api.github.com/repos/Langsch/daily-meditation-mailer/actions/workflows/daily.yml/dispatches`
- todos os dias, 06:00, timezone `America/Sao_Paulo` (confere o timezone, o padrão vem em UTC)
- na aba Advanced: método `POST`, body `{"ref":"main"}` e estes headers:

```
Authorization: Bearer SEU_TOKEN
Accept: application/vnd.github+json
X-GitHub-Api-Version: 2022-11-28
Content-Type: application/json
```

Liga o "notify on failure" do job. Sem o `schedule:` do GitHub como rede de segurança, é o único aviso se o disparo parar.

Pra testar tem o botão TEST RUN: a API responde `204 No Content` e a run aparece no Actions em segundos. Um `404` ali quase sempre é a permissão de Actions faltando no token, o GitHub esconde o recurso em vez de dizer que falta acesso.

O `daily.yml` precisa estar commitado no branch que vai em `ref`. O `workflow_dispatch` só enxerga workflow que já está lá.
