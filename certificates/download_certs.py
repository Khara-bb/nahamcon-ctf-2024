#!/usr/bin/python3
import requests
import json
import logging
import sys
import getopt
import os
from urllib.parse import urljoin, urlparse
from urllib.request import urlretrieve
import re
from tqdm import tqdm
import csv


logging.basicConfig()
logging.root.setLevel(logging.INFO)

os.chdir("/mnt/e/kali/git/nahamcon2024CTF/certificates")

def slugify(text):
    text = re.sub(r"[\s]+", "-", text.lower())
    text = re.sub(r"[-]{2,}", "-", text)
    text = re.sub(r"[^a-z0-9\-]", "", text)
    text = re.sub(r"^-|-$", "", text)
    return text


def main(argv):
    
    if '--help' in '':
        sys.exit()
    else:
        baseUrl, ctfName, outputDir, = "https://ctf.nahamcon.com", "", ""  # defaults?
        headers = {"Content-Type": "application/json"}

        

        apiUrl = urljoin(baseUrl, '/api/v1')

        logging.info("Connecting to API: %s" % apiUrl)
        teams = []

        S = requests.Session()
        # for i in range(1,79):
        #     X = S.get(f"{apiUrl}/teams?page=" + str(i), headers=headers).text
        #     tmp = json.loads(X)
        #     teams.extend(tmp["data"])
        
        # filtered_team = [{'id': entry['id'], 'name': entry['name']} for entry in teams]

        # # Define the CSV file name
        # csv_file = 'filtered_data.csv'

        # # Write the filtered data to a CSV file
        # with open(csv_file, mode='w', newline='') as file:
        #     writer = csv.DictWriter(file, fieldnames=['id', 'name'])
        #     writer.writeheader()
        #     writer.writerows(filtered_team)

        # print(f'Data has been written to {csv_file}')


        logging.info("Retrieved %d teams..." % len(teams))
        csv_file = 'filtered_data.csv'
        # Read the CSV file and generate the list of dictionaries
        with open(csv_file, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            data_from_csv = [row for row in reader]

        # Print the result
        print(data_from_csv)

        burp0_url = "http://challenge.nahamcon.com:31079/"
        burp0_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        sorted_data = sorted(data_from_csv, key=lambda row: int(row['id']))
        for (id, team) in  enumerate(sorted_data):
            team_name = team['name']
            team_id = int(team['id'])
            burp0_data = {"name": team_name}
            if team_id < 1701 :
                print(team_id)
                continue
            response = S.post(burp0_url, headers=burp0_headers, data=burp0_data)
            if response.status_code == 200:
                response_text = response.text

                # Use a regular expression to find the image URL
                match = re.search(r'src="/(static/[^"]+)"', response_text)
                
                if match:
                    img_url = match.group(1)
                    # Form the full URL if the image URL is relative

                    full_img_url = burp0_url + img_url

                    # Download the image
                    img_name = str(team_id).zfill(4)+".png"
                    urlretrieve(full_img_url, img_name)
                    print(f'Image downloaded and saved as {img_name}')
                else:
                    print(str(team_id).zfill(4) + ' Image URL not found for '+ team_name)
            else:
                print(f'POST request failed with status code {response.status_code}')
            
"""
        challs = json.loads(X)

        categories = {}

        logging.info("Retrieved %d challenges..." % len(challs['data']))

        desc_links = []

        for chall in challs['data']:

            Y = json.loads(S.get(f"{apiUrl}/challenges/{chall['id']}", headers=headers).text)["data"]

            if Y["category"] not in categories:
                categories[Y["category"]] = [Y]
            else:
                categories[Y["category"]].append(Y)

            catDir = os.path.join(outputDir, "challenges", Y["category"])
            challDir = os.path.join(catDir, slugify(Y["name"]))

            os.makedirs(challDir, exist_ok=True)
            os.makedirs(catDir, exist_ok=True)

            with open(os.path.join(challDir, "README.md"), "w") as chall_readme:
                logging.info("Creating challenge readme: %s" % Y["name"])
                chall_readme.write("# %s\n\n" % Y["name"])
                chall_readme.write("## Description\n\n%s\n\n" % Y["description"])

                files_header = False

                # Find links in description
                links = re.findall(r'(https?://[^\s]+)', Y["description"])

                if len(links) > 0:
                    for link in links:
                        desc_links.append((Y["name"], link))

                # Find MD images in description
                md_links = re.findall(r'!\[(.*)\]\(([^\s]+)\)', Y["description"])

                if len(md_links) > 0:
                    for link_desc, link in md_links:
                        dl_url = urljoin(baseUrl, link)

                        F = S.get(dl_url, stream=True)

                        fname = urlparse(f_url).path.split("/")[-1]

                        if link[0] in ["/", "\\"]:
                            link = link[1:]

                        local_f_path = os.path.join(outputDir, link)
                        os.makedirs(os.path.join(outputDir, os.path.dirname(link)), exist_ok=True)

                        total_size_in_bytes = int(F.headers.get('content-length', 0))
                        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, desc=fname)

                        with open(local_f_path, "wb") as LF:
                            for chunk in F.iter_content(chunk_size=1024):
                                if chunk:
                                    progress_bar.update(len(chunk))
                                    LF.write(chunk)
                            LF.close()

                        progress_bar.close()

                if "files" in Y and len(Y["files"]) > 0:

                    if not files_header:
                        chall_readme.write("## Files\n\n")

                    challFiles = os.path.join(challDir, "files")
                    os.makedirs(challFiles, exist_ok=True)

                    for file in Y["files"]:

                        # Fetch file from remote server
                        f_url = urljoin(baseUrl, file)
                        F = S.get(f_url, stream=True)

                        fname = urlparse(f_url).path.split("/")[-1]
                        local_f_path = os.path.join(challFiles, fname)

                        chall_readme.write("* [%s](files/%s)\n\n" % (fname, fname))

                        total_size_in_bytes = int(F.headers.get('content-length', 0))
                        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, desc=fname)

                        with open(local_f_path, "wb") as LF:
                            for chunk in F.iter_content(chunk_size=1024):
                                if chunk:
                                    progress_bar.update(len(chunk))
                                    LF.write(chunk)
                            LF.close()

                        progress_bar.close()

                chall_readme.close()

        with open(os.path.join(outputDir, "README.md"), "w") as ctf_readme:

            logging.info("Writing main CTF readme...")

            ctf_readme.write("# %s\n\n" % ctfName)
            ctf_readme.write("## About\n\n[insert description here]\n\n")
            ctf_readme.write("## Challenges\n\n")

            for category in categories:
                ctf_readme.write("### %s\n\n" % category)

                for chall in categories[category]:

                    chall_path = "challenges/%s/%s/" % (chall['category'], slugify(chall['name']))
                    ctf_readme.write("* [%s](%s)" % (chall['name'], chall_path))

                    if "tags" in chall and len(chall["tags"]) > 0:
                        ctf_readme.write(" <em>(%s)</em>" % ",".join(chall["tags"]))

                    ctf_readme.write("\n")

            ctf_readme.close()

        logging.info("All done!")

        if len(desc_links) > 0:
            logging.warning("** Warning, the following links were found in challenge descriptions, you may need to download these files manually.")
            for cname, link in desc_links:
                logging.warning("%s - %s" % (cname, link))
"""

if __name__ == "__main__":
    main(sys.argv[1:])