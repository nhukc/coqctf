import socket
import subprocess
import os
import signal

HOST = '0.0.0.0'  # Listen on all available interfaces
PORT = 12345      # Arbitrary non-privileged port
THEOREM_STATEMENT = "Theorem add_comm : forall a b : nat, a + b = b + a."

def verify_proof(proof_file):
    """Function to verify the submitted Coq proof."""
    try:
        # Run the Coq verifier with a timeout to prevent infinite loops
        result = subprocess.run(
            ['coqc', proof_file], 
            capture_output=True, 
            text=True, 
            check=True,
            timeout=10  # 10 seconds timeout for proof verification
        )
        return "Proof is valid!\n"
    except subprocess.CalledProcessError as e:
        return f"Proof is invalid or incomplete.\n{e.stderr}\n"
    except subprocess.TimeoutExpired:
        return "Proof verification timed out. Please optimize your proof.\n"

def validate_proof_content(proof_content):
    """Check proof content for cheating or disallowed content."""
    # Check if the theorem statement is present
    if THEOREM_STATEMENT not in proof_content:
        return False, "Submitted proof does not match the required theorem statement.\n"
    
    # Check for disallowed tactics or commands
    disallowed_patterns = ["Abort", "admit", "Admitted"]
    for pattern in disallowed_patterns:
        if pattern in proof_content:
            return False, f"Use of disallowed pattern detected: {pattern}\n"
    
    return True, ""

def handle_client(client_socket):
    """Handle incoming client connections."""
    try:
        with client_socket:
            client_socket.sendall(b"Submit your Coq proof:\n")
            proof_data = client_socket.recv(4096).decode('utf-8')

            # Validate the content of the submitted proof
            valid, message = validate_proof_content(proof_data)
            if not valid:
                client_socket.sendall(message.encode('utf-8'))
                return
            
            with open("submitted_proof.v", "w") as proof_file:
                proof_file.write(proof_data)
            
            result = verify_proof("submitted_proof.v")
            client_socket.sendall(result.encode('utf-8'))
    finally:
        # Clean up proof file after verification
        if os.path.exists("submitted_proof.v"):
            os.remove("submitted_proof.v")

def start_server():
    """Start the TCP server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Server listening on {HOST}:{PORT}")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Accepted connection from {addr}")
            handle_client(client_socket)

if __name__ == "__main__":
    start_server()

