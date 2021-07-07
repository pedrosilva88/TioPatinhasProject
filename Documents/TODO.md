- Configuar a Strategy para UK no StrategyConfigFactory
  - as horas de execução posso querer que sejam diferentes
  - devia ter também a opção se quero ter market orders ou limit orders

- A Base de dados de Fills devia guardar a estrategia e o country

- Devia ter um max budget para cada Strategy e ainda um Max Budget para investir por cada Stock dessa estratégia




- Create Orders
       * O o serviço Interactive Broker por vezes pode cancelar as orders que tenho de TakeProfit e StopLoss de um dia para o outro. Podia ter uma action só para criar as Orders dando um stocks
       * Exemple: `python main.py create_orders_for_position AAPL`

- Look to `News`
       * Olhar para noticias e perceber se têm um ranking. E apartir disso tomar decisoesse faz sentido apostar ou não.

- Create Order Issue
       * Neste momento o createOrder só permite criar `LimitOrder`. Era interessante poder criar pelo menos `MarketOrder`.

- Select `ECN`
       * Ter uma lógica para escolher o `ECN` em vez de ser o `SMART`.
       * Nem que seja para já o `BYX`
       * Ver a aula do Mohsen onde explica as `ECN` e as suas `Fees`

- Multi Country
       * UK:
              - Arranque do Script: 07:45
              - Abre: 8:00
              - Startegy Ate: 8:15
              - Cancel All: 11:00

       * USA:
              - Arranque do Script: 14:15
              - Abre: 14:30
              - Startegy Ate: 14:45
              - Cancel All: 17:30

       * Japan - Tokyo:
              - Arranque do Script: 23:45
              - Abre: 00:00
              - Startegy Ate: 00:15
              - Cancel All: 03:00
              - Closes: 06:00

       * Shangai:
              - Arranque do Script: 01:15
              - Abre: 01:30
              - Startegy Ate: 01:45
              - Cancel All: 03:00
              - Closes: 05:00

       * India
              - Arranque do Script: 03:30
              - Abre: 03:45
              - Startegy Ate: 04:00
              - Cancel All: 07:00

- Bot de Telegram
       * Receber informação (Saldo, Positions, Orders)
              * Estado das orders/positions
       * Enviar Acçoes (Cancelar Tudo, Desligar o Script, Resetar o script)
       * Reports

- Base de dados local.
       * Ia guardando dados recollhidos ao longo do decorrer do script.
       * Saldo, Compras, Vendas, Preços...
       * Pode ser interessante para gerar relatorios

- Package de Reports
       * Este pack olharia para uma eventual BD e apartir daí gerava os relatórios.
       * Podiam também ser enviados por email, para o bot telegram
       * Exportar em CSV.
