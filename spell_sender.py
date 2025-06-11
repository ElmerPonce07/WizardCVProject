# spell_sender.py
import socket

def send_spell_to_unity(spell):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(spell.encode(), ("127.0.0.1", 5005))
