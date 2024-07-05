## Script de Backup e Envio para AWS S3

### Introdução

Este script Python realiza backup de arquivos locais em diretórios específicos e os envia para um bucket do Amazon S3, além de fazer cópias locais dos arquivos de backup.

### Instruções de Uso

1. **Configuração Inicial:**
   - Instale Python no ambiente onde o script será executado.
   - Execute `pip install boto3` para instalar dependências.
   - Garanta que `settings.json` e `directories_set.json` estejam configurados corretamente.

2. **Configuração dos Arquivos de Configuração:**
   - **settings.json:**
     - Define parâmetros como intervalo de polling e tempo de inserção no bucket.
   - **directories_set.json:**
     - Lista diretórios locais e de backup para operações.

3. **Credenciais:**
   - As credenciais da AWS são gerenciadas pelo arquivo `lib_credentials.py`.

4. **Execução do Script:**
   - Execute `backup_to_s3.py`.
   - Verifica diretórios em `directories_set.json`, lista e envia arquivos para S3.
   - Realiza cópias locais dos arquivos de backup.

5. **Monitoramento e Logs:**
   - Gera logs detalhados das operações, incluindo sucesso, falhas e erros.

6. **Configuração de Tempo:**
   - Ajuste intervalos de polling e tempo de inserção em `settings.json`.

### Observações

- Configure `settings.json` e `directories_set.json` antes de executar.
- Monitore os logs para verificar o status das operações.
- Requer conhecimento básico em Python e AWS.

---

## Backup and Upload Script for AWS S3

### Introduction

This Python script backs up local files from specific directories and uploads them to an Amazon S3 bucket, while also making local copies of backup files.

### Usage Instructions

1. **Initial Setup:**
   - Install Python in the environment where the script will run.
   - Run `pip install boto3` to install dependencies.
   - Ensure `settings.json` and `directories_set.json` are correctly configured.

2. **Configuration Files Setup:**
   - **settings.json:**
     - Defines parameters like polling interval and bucket insertion time.
   - **directories_set.json:**
     - Lists local and backup directories for operations.

3. **Credentials:**
   - AWS credentials are managed by `lib_credentials.py`.

4. **Running the Script:**
   - Execute `backup_to_s3.py`.
   - Checks directories in `directories_set.json`, lists and uploads files to S3.
   - Makes local copies of backup files.

5. **Monitoring and Logs:**
   - Generates detailed logs of operations, including successes, failures, and errors.

6. **Time Configuration:**
   - Adjust polling intervals and insertion times in `settings.json`.

### Notes

- Configure `settings.json` and `directories_set.json` before execution.
- Monitor logs to track operation status.
- Requires basic knowledge of Python and AWS.