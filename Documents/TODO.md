
- Update Orders
       * Validar se há novos dados a serem atualizados
              * Main Order ✅
              * Profit Order ✅
              * Stop Loss Order ✅
       * Devia validar se compensa investir na stock mesmo que exista GAP. 
              * Se o lastPrice for muito proximo do valor de fecho pode já não compensar

- Look to `Volume` and `News`
       * Tenho que perceber se o `volume` é muito a cima do habitual
       * Tenho que perceber se houve anuncio de `Earnings` ou `Dividens`
       * Olhar para noticias e perceber se têm um ranking. E apartir disso tomar decisoesse faz sentido apostar ou não.

- Look at `Bid/Ask`
       * Para definir o `lmtPrice` que coloco na Order ✅
       * Atualizar o `LmtPrice` de uma Order olhando para o `LastBid` & `LastAsk` ✅

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
       * Devo ter uma logica de timeout para o script "descansar" e acordar quando for necessario. Exemplo: UK começa às 8:30 e o script teria que estar atento até ao 12:30h, depois poderia estar em standby até às 14:30h que é a hora que a exchange de USA abre.

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