Código fonte de um programa que realiar o backup de um banco de dados recocrrente e mandar para o google drive
Esse código foi pensando para ser compilado em um executável pelo PyInstaller

    - ```Realiza o backup do banco de dados MySQL/MariaDB ```
    
    - ```Cria uma tarefa no agendador de tarefas do windows para fazer o backup mensalmente ```
    
    - ```Apaga o Backup do mês anterior do drive ```
    
    - ```Sobe o novo arquivo atualizado ```

*OBS: Para que a função de criar a tarefa no agendador de tarefas seja criada, dentro do .ini precisa estar como 0 no campo VALIDAÇÃO/AGENDADOR e o executável precisa ser executado como Adminstrador no windows,após isso todos mes ira fazer o Backup automaticamente

*OBS2: As credencias do google drive estavam armazenadas direto no código na variavel CRE, da pra fazer do mesmo jeito ou armazenar em um json externo, vai precisar de algumas mudanças
