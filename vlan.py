import os
import subprocess
import colorama
from colorama import Fore, Style
from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks.networking import netmiko_send_config

nr = InitNornir(config_file="config.yaml")

def deploy_vlan(task):
    task.run(task=netmiko_send_config, config_file=f"desired-configs/vlans/{task.host}.txt")
def show_vlan(task):
    task.run(task=netmiko_send_command, command_string="show vlan brief")

current = "pyats learn vlan --testbed-file testbed.yaml --output vlan-current"
os.system(current)
command = subprocess.run(["pyats", "diff", "desired-vlan/", "vlan-current", "--output", "vlandiff"], stdout=subprocess.PIPE)
stringer = str(command)
if "Diff can be found" in stringer:
    clear_command = "clear"
    os.system(clear_command)
    print(Fore.CYAN + "#" * 70)
    print(Fore.RED + "ALERT: " + Style.RESET_ALL + "CURRENT VLAN CONFIGURATIONS ARE NOT IN SYNC WITH DESIRED STATE!")
    print(Fore.CYAN + "#" * 70)
    print("\n")
    answer = input(Fore.YELLOW + "Would you like to reverse the current VLAN configuration back to its desired state? " + Style.RESET_ALL + "<y/n>: ")
    if answer == "y":
        def main() -> None:
            clear_command = "clear"
            clean_up = "rm -r vlandiff vlan-current"
            os.system(clean_up)
            os.system(clear_command)
            nr = InitNornir(config_file="config.yaml")
            targets = nr.filter(device="switch")
            result = targets.run(task=deploy_vlan)
            output = targets.run(task=show_vlan)
            print_title("REVERSING VLAN CONFIGURATION BACK INTO DESIRED STATE")
            print_result(output)

        if __name__ == '__main__':
                main()

else:
    clean_up = "rm -r vlandiff vlan-current"
    os.system(clean_up)
    print("\n")
    print("~" * 50)
    print(Fore.GREEN + "Good news! VLANS are matching desired state!" + Style.RESET_ALL)
    print("~" * 50)
