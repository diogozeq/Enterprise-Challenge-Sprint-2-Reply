import os

def concatenate_files():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    output_file = os.path.join(os.path.dirname(__file__), 'todos_os_codigos.txt')
    
    # Extensões de arquivos que geralmente contêm texto (e.g., código, config, doc)
    text_file_extensions = (
        '.cpp', '.h', '.ino', '.json', '.toml', '.ini', '.py', '.txt', '.bat', '.md',
        '.c', '.hpp', '.js', '.ts', '.css', '.html', '.xml', '.yaml', '.yml',
        '.sh', '.ps1', '.sql', '.graphql', '.log', '.csv', '.tsv',
        '.env', '.gitignore', '.code-workspace',
    )
    
    # Pastas e arquivos a serem explicitamente ignorados
    # Adicionado `.pio` e `.vscode` porque geralmente contêm arquivos de build/configuração específicos do ambiente
    ignored_paths = [
        os.path.join(project_root, '.git'),
        os.path.join(project_root, '.pio'),
        os.path.join(project_root, '.vscode'),
        output_file, # Ignora o próprio arquivo de saída
        os.path.abspath(__file__), # Ignora o próprio script de concatenação
    ]

    # Arquivos binários para ignorar explicitamente, independentemente da extensão
    # Adicionado .bin, .elf, .jpg, .jpeg, .png, .gif, .bmp, .svg, .ico, .pdf, .zip, .rar, .7z, .exe, .dll, .obj, .lib, .a, .so, .dylib
    ignored_binary_files = ('firmware.bin', 'firmware.elf')

    print("Iniciando a concatenação de todos os arquivos de código e texto do projeto...")
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write("=" * 80 + "\n")
        outfile.write("HERMES REPLY - ENTERPRISE CHALLENGE SPRINT 2\n")
        outfile.write("Autor: Diogo Leite Zequini Pinto - RM: 565535\n")
        outfile.write("Todos os códigos e arquivos de texto do projeto concatenados\n")
        outfile.write("=" * 80 + "\n\n")
        
        for root, dirs, files in os.walk(project_root):
            # Ignorar diretórios específicos
            dirs[:] = [d for d in dirs if os.path.join(root, d) not in ignored_paths and not d.startswith('.')]
            
            for file_name in files:
                file_path = os.path.join(root, file_name)
                
                # Ignorar arquivos específicos ou binários
                if file_path in ignored_paths or file_name in ignored_binary_files:
                    continue

                # Ignorar se o arquivo não tem extensão de texto ou é binário
                if not file_name.lower().endswith(text_file_extensions):
                    # Tentativa de detectar binários por conteúdo (simplificado)
                    try:
                        with open(file_path, 'rb') as f:
                            header = f.read(512) # Ler os primeiros 512 bytes
                            if b'\x00' in header: # Se encontrar byte nulo, provavelmente é binário
                                print(f"Ignorando arquivo binário detectado: {file_path}")
                                continue
                    except Exception as e:
                        print(f"Erro ao verificar {file_path} (pode ser binário): {e}")
                        continue # Assume que é binário ou inacessível
                    
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        outfile.write(f"\n{'='*60}\n")
                        outfile.write(f"ARQUIVO: {os.path.relpath(file_path, project_root)}\n")
                        outfile.write(f"{'='*60}\n\n")
                        outfile.write(infile.read())
                        outfile.write("\n\n")
                    print(f"Adicionado: {os.path.relpath(file_path, project_root)}")
                except UnicodeDecodeError:
                    print(f"Ignorando arquivo não-UTF-8 ou binário: {os.path.relpath(file_path, project_root)}")
                except Exception as e:
                    print(f"Erro ao processar {os.path.relpath(file_path, project_root)}: {e}")

    print(f"Processo de concatenação concluído. Verifique '{os.path.relpath(output_file, project_root)}'")

if __name__ == "__main__":
    concatenate_files() 