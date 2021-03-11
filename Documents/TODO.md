
- Bugs
       - GTIM - Nesta Stock aconteceu que bateu num OPG para short entao criou uma order. Entretanto o valor desceu tanto que já ultrapasou o profit que eu criei pa essa order. Se essa não for executado e o valor já for muito baixo também deveria cancelar essa order.

- Look to `Volume` and `News`
       * Tenho que perceber se o `volume` é muito a cima do habitual
       * Tenho que perceber se houve anuncio de `Earnings` ou `Dividens`
       * Olhar para noticias e perceber se têm um ranking. E apartir disso tomar decisoesse faz sentido apostar ou não.

- Calcular `comissions`
       * Preciso saber quanto uma order me vai custar, antes de a executar. Isto porque pode não compensar executar essa order.

- Usar o `cancelMktData` para deixar de escutar uma derterminada stock
       * Isto aqui tem de ser mais inteligente. Se mudar de dia tenho que restar a lista de stocks.

- Create Order Issue
       * Neste momento o createOrder só permite criar `LimitOrder`. Era interessante poder criar pelo menos `MarketOrder`.

- Select `ECN` 
       * Ter uma lógica para escolher o `ECN` em vez de ser o `SMART`. 
       * Nem que seja para já o `BYX`
       * Ver a aula do Mohsen onde explica as `ECN` e as suas `Fees`

- Stock(ticker, `SMART`, `USD`)
       * Perceber como posso ter a currency dinamica
       * Se tiver a criar uma `Stock USA` tem de ser `USD` se for uma `Stock UK` tem que ser `POUND`

- Multi Country
       * Implementar lógica para conseguir correr em vários países diferentes horas. Podia começar por UK e USA.
       * Devo ter uma logica de timeout para o script "descansar" e acordar quando for necessario. Exemplo: UK começa às 8:00 e o script teria que estar atento até ao 12:30h, depois poderia estar em standby até às 14:30h que é a hora que a exchange de USA abre.

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

- Bugs
       - Houve um caso da VUZI a (03/08) em que começou com um GAP de short e passado 2 minutos desceu tanto que o GAP passou a ser de LONG. ✅
              * O bug que aconteceu foi que ao minuto 1 eu criei uma order de SELL e no minuto 2 os lmtPrices dessa orders foram atualizados para  valores de BUY, mas o tipo da action não muda, só muda os lmtPrices e Sizes. ✅
              * Ou seja, aqui preciso também analisar se o lmtPrice faz sentido atualizar ou até mesmo criar ✅
       - Uma das que apostei mais uma vez teve earning na sua abertura. ✅
              * É muito importante validar isso ✅
       - Há também a questão do Total Cash. O valor quando tenho várias apostas não parece correto. ✅
              * Pode ter a ver com as apostas de Short em que o broker tira dinheiro para "maintenance" ✅

- Update Orders ✅
       * Validar se há novos dados a serem atualizados ✅
              * Main Order ✅
              * Profit Order ✅
              * Stop Loss Order ✅
       * Devia validar se compensa investir na stock mesmo que exista GAP. ✅
              * Se o lastPrice for muito proximo do valor de fecho pode já não compensar ✅

- Look at `Bid/Ask` ✅
       * Para definir o `lmtPrice` que coloco na Order ✅
       * Atualizar o `LmtPrice` de uma Order olhando para o `LastBid` & `LastAsk` ✅