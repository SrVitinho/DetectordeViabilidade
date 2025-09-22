import requests
import os
import re 
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm 

def find_latest_link(url_base):
    try:
        response = requests.get(url_base)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links_datasets = [
            a['href'] for a in soup.find_all('a', href=True) 
            if re.match(r'\d{4}-\d{2}/', a['href'])
        ]
        
        if not links_datasets:
            print("No valid dataset directory (YYYY-MM/) was found.")
            return None

        most_recent_directory = max(links_datasets)
        print(f"Most recent directory found: {most_recent_directory}")

        return urljoin(url_base, most_recent_directory)

    except requests.exceptions.RequestException as e:
        print(f"Error accessing URL: {e}")
        return None

def download_dataset_files(url_dataset):
    files_to_download = []
    numbered_prefixes = ['Empresas', 'Estabelecimentos']

    for prefix in numbered_prefixes:
        for i in range(10):
            files_to_download.append(f"{prefix}{i}.zip")
    
    files_to_download.append('Simples.zip')

    print(f"\nA total of {len(files_to_download)} files will be downloaded.")

    main_folder = "DadosRF"
    subfolders = ['Empresas', 'Estabelecimentos', 'Simples']
    
    os.makedirs(main_folder, exist_ok=True) 
    for sub in subfolders:
        os.makedirs(os.path.join(main_folder, sub), exist_ok=True)
    
    print(f"Directory structure inside '{main_folder}' is ready.")
    for file_name in files_to_download:
        destination_subfolder = None
        if file_name.startswith('Empresas'):
            destination_subfolder = 'Empresas'
        elif file_name.startswith('Estabelecimentos'):
            destination_subfolder = 'Estabelecimentos'
        elif file_name == 'Simples.zip':
            destination_subfolder = 'Simples'

        if destination_subfolder:
            file_url = urljoin(url_dataset, file_name)
            local_path = os.path.join(main_folder, destination_subfolder, file_name)
            
            print(f"\nDownloading '{file_name}' to '{os.path.join(destination_subfolder, file_name)}'...")
            
            try:
                with requests.get(file_url, stream=True) as r:
                    r.raise_for_status()
                    total_size = int(r.headers.get('content-length', 0))  # tamanho total
                    block_size = 8192
                    progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)

                    with open(local_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=block_size):
                            f.write(chunk)
                            progress_bar.update(len(chunk))

                    progress_bar.close()

                    if total_size != 0 and progress_bar.n != total_size:
                        print(f"Warning: '{file_name}' downloaded size does not match expected.")
                    else:
                        print(f"'{file_name}' saved successfully!")

            except requests.exceptions.RequestException as e:
                print(f"Error downloading the file '{file_name}': {e}")
                continue
        else:
            print(f"Skipping file with unknown type: {file_name}")

    print("\nDownload of all files completed.")

if __name__ == "__main__":
    URL_BASE_RF = "https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/"
    
    recent_url = find_latest_link(URL_BASE_RF)
    
    if recent_url:
        download_dataset_files(recent_url)
