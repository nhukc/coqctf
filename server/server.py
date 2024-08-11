import socket
import subprocess
import os

# Theorems, ports, and flags
theorems = {
    12345: {
        'statement': "Theorem double_negation : forall P : Prop, P -> ~~P.",
        'file_name': "double_negation.v",
        'flag': "CTF{d0uble_n3gation_pr00f}"
    },
    12346: {
        'statement': "Theorem identity_function : forall (A : Type) (x : A), x = x.",
        'file_name': "identity_function.v",
        'flag': "CTF{id3ntity_funCti0n_pr00f}"
    },
    12347: {
        'statement': "Theorem add_zero : forall n : nat, n + 0 = n.",
        'file_name': "add_zero.v",
        'flag': "CTF{additi0n_with_z3r0_pr00f}"
    },
    12348: {
        'statement': "Theorem app_nil_r : forall (A : Type) (l : list A), l ++ [] = l.",
        'file_name': "app_nil_r.v",
        'flag': "CTF{app_n1l_r_pr00f}"
    },
    12349: {
        'statement': "Theorem negb_involutive : forall b : bool, negb (negb b) = b.",
        'file_name': "negb_involutive.v",
        'flag': "CTF{n3gb_involut1ve_pr00f}"
    }
}

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

def validate_proof_content(proof_content, theorem_statement):
    """Check proof content for cheating or disallowed content."""
    # Check if the theorem statement is present
    if theorem_statement not in proof_content:
        return False, "Submitted proof does not match the required theorem statement.\n"
    
    # Check for disallowed tactics or commands
    disallowed_patterns = ["Abort", "admit", "Admitted"]
    for pattern in disallowed_patterns:
        if pattern in proof_content:
            return False, f"Use of disallowed pattern detected: {pattern}\n"
    
    return True, ""

def handle_client(client_socket, theorem_info):
    """Handle incoming client connections."""
    theorem_statement = theorem_info['statement']
    file_name = theorem_info['file_name']
    flag = theorem_info['flag']

    try:
        with client_socket:
            client_socket.sendall(f"Submit your Coq proof for the following theorem:\n{theorem_statement}\n".encode('utf-8'))
            proof_data = client_socket.recv(4096).decode('utf-8')

            # Validate the content of the submitted proof
            valid, message = validate_proof_content(proof_data, theorem_statement)
            if not valid:
                client_socket.sendall(message.encode('utf-8'))
                return
            
            with open(file_name, "w") as proof_file:
                proof_file.write(proof_data)
            
            result = verify_proof(file_name)
            if "Proof is valid!" in result:
                result += f"Congratulations! Here is your flag: {flag}\n"
            client_socket.sendall(result.encode('utf-8'))
    finally:
        # Clean up proof file after verification
        if os.path.exists(file_name):
            os.remove(file_name)

def start_server(port, theorem_info):
    """Start the TCP server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen()
        print(f"Server listening on 0.0.0.0:{port}")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Accepted connection from {addr}")
            handle_client(client_socket, theorem_info)

if __name__ == "__main__":
    import multiprocessing

    processes = []
    for port, theorem_info in theorems.items():
        p = multiprocessing.Process(target=start_server, args=(port, theorem_info))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

