# direct_chat.py – Single-file P2P Chat (Receiver + Client in one)
# Run with: python direct_chat.py
# Supports both LAN and internet (if port 5000 is forwarded)

import socket
import threading
import sys
import time

PORT = 5000
BUFFER_SIZE = 4096

def get_local_ip():
    """Return the most likely local IP address (LAN)"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def clear_line():
    print("\r" + " " * 80 + "\r", end="")

def receiver_mode():
    print("\n" + "="*60)
    print(" DIRECT CHAT – RECEIVER MODE (Waiting for friend)")
    print("="*60)
    print(f"Your IP → {get_local_ip()}  |  Port: {PORT}")
    print("Give this exact IP to your friend.")
    print("Waiting for incoming connection...\n")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", PORT))
    server.listen(1)

    conn, addr = server.accept()
    print(f"CONNECTED! → {addr[0]} joined the chat.\n")
    print("Start typing (type 'exit' to quit)\n")

    def receive_loop():
        while True:
            try:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    print("\n[Friend disconnected]")
                    break
                msg = data.decode("utf-8", errors="ignore")
                # Display friend's message without the "You:" prefix
                if msg.strip().startswith("You:"):
                    print(f"\rFriend: {msg[4:].strip()}")
                else:
                    print(msg, end="")
            except:
                break

    threading.Thread(target=receive_loop, daemon=True).start()

    try:
        while True:
            msg = input()
            if msg.lower() == "exit":
                print("[You left the chat]")
                break
            if msg.strip():
                print(f"You: {msg}")
                conn.sendall(f"You: {msg}\n".encode("utf-8"))
    except:
        print("\n[Connection lost]")
    finally:
        conn.close()
        server.close()

def client_mode():
    print("\n" + "="*60)
    print(" DIRECT CHAT – CLIENT MODE (Connecting to friend)")
    print("="*60)
    ip = input("Enter friend's IP → ").strip()
    if not ip:
        print("No IP entered.")
        return

    print("Connecting", end="")
    for _ in range(3):
        time.sleep(0.6)
        print(".", end="", flush=True)
    print()

    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((ip, PORT))
    except Exception as e:
        print(f"\nCannot connect to {ip}:{PORT}")
        print("• Make sure the receiver is running")
        print("• Check IP address and firewall/port forwarding")
        input("\nPress Enter to return to menu...")
        return

    print(f"\nConnected to {ip}! Start chatting!\n")

    def receive_loop():
        while True:
            try:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    print("\n[Friend disconnected]")
                    break
                msg = data.decode("utf-8", errors="ignore").strip()
                if msg.startswith("You:"):
                    print(f"\rFriend: {msg[4:].strip()}")
                else:
                    print(msg)
            except:
                break

    threading.Thread(target=receive_loop, daemon=True).start()

    try:
        while True:
            msg = input().strip()
            if msg.lower() == "exit":
                print("[You left the chat]")
                break
            if msg:
                print(f"You: {msg}")
                conn.sendall(f"You: {msg}\n".encode("utf-8"))
    except:
        print("\n[Connection lost]")
    finally:
        conn.close()

# ====================== MAIN MENU ======================
def main():
    print("="*60)
    print("        DIRECT P2P CHAT – SINGLE FILE VERSION         ")
    print("="*60)
    print("Type one of the commands below:")
    print()
    print("  scan    →  Run as Receiver (friend connects to you)")
    print("  connect →  Run as Client (you connect to friend)")
    print("  exit    →  Quit the program")
    print()

    while True:
        choice = input("→ ").strip().lower()

        if choice == "scan":
            receiver_mode()
        elif choice == "connect":
            client_mode()
        elif choice in ("exit", "quit"):
            print("Goodbye!")
            break
        else:
            print("Invalid command. Type 'scan', 'connect', or 'exit'.")

        print("\n" + "-"*60)
        print("Returning to main menu...\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nChat terminated by user.")
        sys.exit(0)
