from colorama import Fore, Style


def banner():
    # Display banner
    PURPLE = "\033[38;5;129m"
    GREY = "\033[38;2;192;192;192m"
    RESET = Style.RESET_ALL
    
    return fr'''{PURPLE}                                                                                                    
            ___.    __          
  ________ _\_ |___/  |_  ____  
 /  ___/  |  \ __ \   __\/  _ \ 
 \___ \|  |  / \_\ \  | (  <_> )
/____  >____/|___  /__|  \____/ 
     \/          \/                                                                                                                                                                                               
{RESET}{GREY}Built by: Hunter{RESET}
'''


"""
[*] Scanning 42 subdomains

[!] app.example.com    Potential takeover    Heroku
[-] old.example.com    Not vulnerable    Heroku

Targets: 2 | Potential: 1 | Time: 2.42s
"""


def frame(result):
    Colors = {
        "potential": Fore.LIGHTRED_EX,
        "not_vulnerable": "\033[38;5;245m",
    }

    Reset = Style.RESET_ALL

    target = f"{result['target']:<40}"

    if result["potential"]:
        print(f"{Colors['potential']}[!]{Reset} {target} Potential takeover")
    else:
        print(f"{Colors['not_vulnerable']}[-]{Reset} {target} No takeover detected")