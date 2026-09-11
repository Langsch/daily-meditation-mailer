# opus-dei-meditations

Pega a meditação diária publicada em [opusdei.org/pt-br/meditation](https://opusdei.org/pt-br/meditation/) e manda por email, formatada em HTML.

Roda todo dia via GitHub Actions (não depende de nenhuma máquina ligada). Também dá pra rodar manualmente, uma vez só, local.

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
3. Use essa senha de 16 letras como `GMAIL_APP_PASSWORD` — não é a senha normal da conta.

## Rodar todo dia via GitHub Actions

Em Settings → Secrets and variables → Actions do repo, cria estes secrets:

- `GMAIL_USER` — o email que envia
- `GMAIL_APP_PASSWORD` — a senha de app gerada acima
- `RECIPIENTS` — lista de destinatários separados por vírgula (fica privado, não aparece pra quem olha o repo)

O workflow em `.github/workflows/daily.yml` roda todo dia às 06:00 (horário de Brasília). Pra mudar o horário, ajusta o `cron` no arquivo (horário é sempre UTC). Também dá pra disparar manualmente pela aba Actions → Send daily meditation → Run workflow.
