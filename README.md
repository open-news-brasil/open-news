# Notícias de Parnaíba

Coleta automatizada das últimas notícias de Parnaíba-PI e região, nos principais sites da região. A coleta roda a cada dez minutos e é publicada no canal do Telegram [@noticias_phb](https://t.me/s/noticias_phb), pelo bot [@noticias_phb_bot](https://t.me/noticias_phb_bot) ou alguma de suas réplicas de segurança.

### Portais monitorados

- [carlsonpessoa.blogspot.com](https://carlsonpessoa.blogspot.com)
- [portaldocatita.blogspot.com](https://portaldocatita.blogspot.com)
- [jornaldaparnaiba.com](https://www.jornaldaparnaiba.com)
- [phbemnota.com](https://phbemnota.com)
- [clickparnaiba.blogspot.com](https://clickparnaiba.blogspot.com)
- [plantaoparnaiba24horas.com.br](https://www.plantaoparnaiba24horas.com.br)
- [portaldoaguia.com.br](https://www.portaldoaguia.com.br)
- [portalphb.com.br](https://www.portalphb.com.br)
- [portallitoralnoticias.com.br](https://portallitoralnoticias.com.br)
- [blogdobsilva.com.br](https://blogdobsilva.com.br)

> Gostaria que algum outro portal fosse monitorado? Submeta uma issue [aqui](https://github.com/jjpaulo2/noticias-phb/issues).

## Executando o projeto

Faça o build da imagem Docker.

```shell
docker build --no-cache -t noticias_phb:latest .
```

Depois, execute ela com as variáveis de ambiente necessárias.

```shell
docker run -d \
    --name=noticias-phb \
    --restart=always \
    -e TELEGRAM_API_ID=... \
    -e TELEGRAM_API_HASH=... \
    -e TELEGRAM_BOT_REPLICA_0_TOKEN=... \
    -e TELEGRAM_CHAT_ID=... \
    -v ./data:/srv/data \
    noticias_phb:latest
```

Você pode informar o até 4 tokens de bot. Esses tokens são usados para rotação, caso a API do Telegram retorne `FloodWaitError`.
