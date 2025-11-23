import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from typing import List, Dict, Optional

import subprocess
import threading
import shutil
import os

# Ajuste aqui: nome do script que inicia seu compilador (o arquivo que você executa para compilar .txt)
# Ex.: "run_compiler.py" ou "main_compiler.py" — coloque o nome correto do seu projeto
COMPILER_SCRIPT = "main.py"

# pasta onde salvamos os .obj compilados
OUTPUTS_DIR = os.path.join(os.getcwd(), "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

class Instruction:
    def __init__(self, op, args=None):
        self.op = op                # Nome da instrução (ex: ADD, LDC, ALLOC)
        self.args = args or []      # Lista de argumentos (ex: [0, 3])

    def __repr__(self):             # exibe instrução na inferfacie de usuario
        if self.args:
            return f"{self.op} {self.args}"
        return self.op


class MVDMachine:
    def __init__(self, program: List[Instruction]):
        self.P = program
        self.M: Dict[int, int] = {}
        self.i = 0
        self.s = -1
        self.running = False
        self.waiting_for_input = False
        self.halted = False

    def reset(self):
        self.M.clear()
        self.i = 0
        self.s = -1
        self.running = False
        self.waiting_for_input = False
        self.halted = False

    def _get(self, addr: int) -> int:
        return self.M.get(addr, 0)

    def _set(self, addr: int, value: int):
        self.M[addr] = int(value)

    def step(self) -> str:
        """Executa uma instrução. Retorna:
        - 'ok' se executou normalmente e continua
        - 'halt' se encontrou HLT
        - 'need_input' se encontrou RD e precisa de valor
        - 'prn' se imprimiu um valor (valor em self._last_prn)
        """
        if self.halted:
            return 'halt'

        if not (0 <= self.i < len(self.P)):
            self.halted = True
            return 'halt'

        instr = self.P[self.i]
        op = instr.op
        a = instr.args  # lista de argumentos posicionais

        # por padrão, próxima instrução
        next_i = self.i + 1

        # START
        if op == 'START':
            self.s = -1

        elif op in ('HLT', 'HL'):
            self.halted = True
            return 'halt'

        elif op == 'LDC':
            k = a[0]
            self.s += 1
            self._set(self.s, k)

        elif op == 'LDV':
            n = a[0]
            self.s += 1
            self._set(self.s, self._get(n))

        elif op == 'STR':
            n = a[0]
            self._set(n, self._get(self.s))
            self.s -= 1

        elif op == 'ALLOC':
            m, n = a[0], a[1]
            for k in range(n):
                self.s += 1
                self._set(self.s, self._get(m + k))

        elif op == 'DALLOC':
            m, n = a[0], a[1]
            for k in range(n-1, -1, -1):
                self._set(m + k, self._get(self.s))
                self.s -= 1

        elif op == 'CALL':
            p = a[0]
            self.s += 1
            self._set(self.s, self.i + 1)
            next_i = p

        elif op == 'RETURN':
            ret_addr = self._get(self.s)
            self.s -= 1
            next_i = ret_addr

        elif op == 'JMP':
            next_i = a[0]

        elif op == 'JMPF':
            p = a[0]
            cond = self._get(self.s)
            self.s -= 1
            if cond == 0:
                next_i = p

        elif op == 'RD':
            # sinaliza que precisa de input e NÃO avança i
            self.waiting_for_input = True
            return 'need_input'

        elif op == 'PRN':
            # pega valor do topo, guarda em _last_prn e decrementa s
            value = self._get(self.s)
            self.s -= 1
            self._last_prn = value
            # avança PC e informa GUI que houve uma impressão
            self.i = next_i
            return 'prn'

        elif op == 'ADD':
            v1 = self._get(self.s-1); v2 = self._get(self.s)
            self._set(self.s-1, v1 + v2)
            self.s -= 1

        elif op == 'SUB':
            v1 = self._get(self.s-1); v2 = self._get(self.s)
            self._set(self.s-1, v1 - v2)
            self.s -= 1

        elif op == 'MULT':
            v1 = self._get(self.s-1); v2 = self._get(self.s)
            self._set(self.s-1, v1 * v2)
            self.s -= 1

        elif op == 'DIVI':
            v1 = self._get(self.s-1); v2 = self._get(self.s)
            if v2 == 0:
                raise ZeroDivisionError('DIVI por zero')
            self._set(self.s-1, v1 // v2)
            self.s -= 1

        elif op == 'INV':
            v = self._get(self.s)
            self._set(self.s, -v)

        elif op == 'AND':
            v1 = self._get(self.s-1); v2 = self._get(self.s)
            self._set(self.s-1, 1 if (v1 == 1 and v2 == 1) else 0)
            self.s -= 1

        elif op == 'OR':
            v1 = self._get(self.s-1); v2 = self._get(self.s)
            self._set(self.s-1, 1 if (v1 == 1 or v2 == 1) else 0)
            self.s -= 1

        elif op == 'NEG':
            v = self._get(self.s)
            self._set(self.s, 1 - (1 if v != 0 else 0))

        elif op == 'CME':
            v1 = self._get(self.s-1); v2 = self._get(self.s)
            self._set(self.s-1, 1 if v1 < v2 else 0)
            self.s -= 1

        elif op == 'CMA':
            v1 = self._get(self.s-1); v2 = self._get(self.s)
            self._set(self.s-1, 1 if v1 > v2 else 0)
            self.s -= 1

        elif op == 'CEQ':
            v1 = self._get(self.s-1); v2 = self._get(self.s)
            self._set(self.s-1, 1 if v1 == v2 else 0)
            self.s -= 1

        elif op == 'CDIF':
            v1 = self._get(self.s-1); v2 = self._get(self.s)
            self._set(self.s-1, 1 if v1 != v2 else 0)
            self.s -= 1

        elif op == 'CMEQ':
            v1 = self._get(self.s-1); v2 = self._get(self.s)
            self._set(self.s-1, 1 if v1 <= v2 else 0)
            self.s -= 1

        elif op == 'CMAQ':
            v1 = self._get(self.s-1); v2 = self._get(self.s)
            self._set(self.s-1, 1 if v1 >= v2 else 0)
            self.s -= 1

        elif op == 'NULL':
            pass
        
        
        # atualiza i e retorna ok
        self.i = next_i
        return 'ok'
           



    def provide_input(self, val: int):
        """Fornece valor para a instrução RD previamente encontrada.
        Após chamar, a máquina avança i normalmente.
        """
        if not self.waiting_for_input:
            raise RuntimeError('Máquina não está aguardando input')
        self.s += 1
        self._set(self.s, int(val))
        self.waiting_for_input = False
        self.i = self.i + 1  # avança após RD

        if self.halted:
            return 'halt'

        if not (0 <= self.i < len(self.P)):
            self.halted = True
            return 'halt'

        instr = self.P[self.i]
        op = instr.op
        a = instr.args

            # por padrão
        next_i = self.i + 1

           
# -----------------------------
# Parser
# -----------------------------

def parse_obj_text(text: str): #tranforma o obj em instrucoes
    lines = text.splitlines()
    raw_lines = []
    label_to_addr = {}
    pc = 0
    # 1ª passada: detectar labels e endereços (agora mais robusta)
    for original_line in lines:
        line = original_line.strip()
        tokens = line.split() #separa labels, opcodes e args
        if not tokens:
            continue

        #inicia valores
        label = None
        opcode = None
        arg_text = ''

        # Caso 1: label seguido de NULL -> "2 NULL"
        if len(tokens) > 1 and tokens[1] == "NULL":
            label = tokens[0]        # a label
            opcode = "NULL"          # o opcode REAL
            arg_text = ""            # sem argumentos
        # Caso 2: opcode sozinho (ex: "START" ou "HLT")
        elif len(tokens) == 1:
            tok = tokens[0]
            opcode = tok
            arg_text = ''
        # Caso 3: linha que começa com opcode (normal)
        else:
            opcode = tokens[0]
            arg_text = ' '.join(tokens[1:])

        # addr aponta para a próxima instrução (ou para a instrução atual, caso exista)
        addr = pc
        pc += 1

        if label is not None:
            # mapeia label -> endereço (endereço da próxima instrução)
            label_to_addr[label] = addr

        raw_lines.append((label, opcode, arg_text, addr))

    # 2ª passada: construir instruções a partir de raw_lines
    program = []

    for (label, opcode, arg_text, addr) in raw_lines:
        op = opcode
        args = []
        text_args = arg_text.strip()

        # Função simples: extrai inteiros na ordem
        def extract_ints(t):
            return [int(x) for x in t.split()]
        
        # ---- Instruções com labels ----
        if op in ("JMP", "JMPF", "CALL"):
            lbl = text_args.split()[0]            # nome da label
            args = [label_to_addr[lbl]]           # coloca o endereço resolvido na lista

        # ---- Instruções numéricas ----
        elif op in ("LDC", "LDV", "STR","ALLOC", "DALLOC"):
            args = extract_ints(text_args) 

        # ---- Instruções sem argumentos ----
        else:
            args = []                              # ex: ADD, MULT, HLT, RETURN, START

        program.append(Instruction(op=op, args=args))

    print(program)
    return program

   

# -----------------------------
# GUI
# -----------------------------

class MVDGUI:
    def __init__(self, root):
        self.root = root
        root.title('MVD - Máquina Virtual Didática (GUI)')

        # frames
        top_frame = tk.Frame(root)
        top_frame.pack(fill='x')
        btn_compile = tk.Button(top_frame, text='Compile .txt', command=self.choose_and_compile)
        btn_compile.pack(side='left', padx=4, pady=4)

        btn_load = tk.Button(top_frame, text='Load .obj', command=self.load_file)
        btn_load.pack(side='left', padx=4, pady=4)

        btn_reset = tk.Button(top_frame, text='Reset VM', command=self.reset_vm)
        btn_reset.pack(side='left', padx=4)

        self.btn_step = tk.Button(top_frame, text='Run', command=self.on_step)
        self.btn_step.pack(side='left', padx=4)
        # main panes
        middle = tk.PanedWindow(root, orient='horizontal')
        middle.pack(fill='both', expand=True)

        # editor / program text
        left = tk.Frame(middle)
        middle.add(left, minsize=380)
        tk.Label(left, text='Programa (.obj)').pack(anchor='w')
        self.txt_prog = scrolledtext.ScrolledText(left, width=60, height=25)
        self.txt_prog.pack(fill='both', expand=True)

        # direita: estado e IO
        right = tk.Frame(middle)
        middle.add(right, minsize=300)

        reg_frame = tk.Frame(right)
        reg_frame.pack(fill='x', pady=4)
        tk.Label(reg_frame, text='Registradores:').pack(anchor='w')
        self.lbl_i = tk.Label(reg_frame, text='i: 0')
        self.lbl_i.pack(anchor='w')
        self.lbl_s = tk.Label(reg_frame, text='s: -1')
        self.lbl_s.pack(anchor='w')

        tk.Label(right, text='Pilha / Memória (endereços usados)').pack(anchor='w')
        self.lst_mem = tk.Listbox(right, width=40, height=12)
        self.lst_mem.pack(fill='both', expand=False)

        io_frame = tk.Frame(right)
        io_frame.pack(fill='both', expand=True, pady=4)
        tk.Label(io_frame, text='Output (PRN):').pack(anchor='w')
        self.txt_out = scrolledtext.ScrolledText(io_frame, height=6)
        self.txt_out.pack(fill='both', expand=True)

        in_frame = tk.Frame(io_frame)
        in_frame.pack(fill='x', pady=4)
        tk.Label(in_frame, text='Input (RD):').pack(side='left')
        self.entry_input = tk.Entry(in_frame, width=12)
        self.entry_input.pack(side='left', padx=4)
        self.btn_send_input = tk.Button(in_frame, text='Send Input', command=self.send_input)
        self.btn_send_input.pack(side='left')

        status_frame = tk.Frame(right)
        status_frame.pack(fill='x')
        self.lbl_status = tk.Label(status_frame, text='Status: idle')
        self.lbl_status.pack(anchor='w')

        # VM internal
        self.vm: Optional[MVDMachine] = None
        self.program_loaded = False
        self.auto_running = False

        # polling
        self.root.after(200, self._periodic_update)

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[('OBJ files', '*.obj'), ('All files', '*.*')])
        if not path:
            return
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        self.txt_prog.delete('1.0', tk.END)
        self.txt_prog.insert('1.0', text)
        try:
            program = parse_obj_text(text)
        except Exception as e:
            messagebox.showerror('Parser error', str(e))
            return
        self.vm = MVDMachine(program)
        self.program_loaded = True
        self.update_gui()
        self.lbl_status.config(text=f'Loaded: {path}')

    def reset_vm(self):
        if not self.program_loaded:
            messagebox.showinfo('Info', 'Nenhum programa carregado')
            return
        self.vm.reset()
        self.auto_running = False
        self.update_gui()
        self.lbl_status.config(text='Reset realizado')

    def on_step(self):
        if not self.program_loaded:
            messagebox.showinfo('Info', 'Nenhum programa carregado')
            return
        try:
            res = self.vm.step()
        except Exception as e:
            messagebox.showerror('Erro execução', str(e))
            self.auto_running = False
            return

        if res == 'ok':
            pass
        elif res == 'halt':
            self.lbl_status.config(text='Status: halted')
            messagebox.showinfo('HLT', 'Programa finalizado (HLT)')
        elif res == 'need_input':
            self.lbl_status.config(text='Aguardando RD (forneça input)')
        elif res == 'prn':
            # pegar último PRN
            val = getattr(self.vm, '_last_prn', None)
            if val is not None:
                self.txt_out.insert(tk.END, str(val) + '\n')
                self.txt_out.see(tk.END)

        self.update_gui()

        

    def send_input(self):
        if not self.program_loaded or not self.vm.waiting_for_input:
            messagebox.showinfo('Info', 'Máquina não está aguardando input (RD)')
            return
        txt = self.entry_input.get().strip()
        if not txt:
            messagebox.showinfo('Input', 'Digite um inteiro')
            return
        try:
            val = int(txt)
        except ValueError:
            messagebox.showerror('Erro', 'Digite um inteiro válido')
            return
        try:
            self.vm.provide_input(val)
        except Exception as e:
            messagebox.showerror('Erro', str(e))
            return
        self.entry_input.delete(0, tk.END)
        self.lbl_status.config(text='Input fornecido')
        self.update_gui()

    def update_gui(self):
        if not self.program_loaded:
            self.lbl_i.config(text='i: -')
            self.lbl_s.config(text='s: -')
            self.lst_mem.delete(0, tk.END)
            return
        self.lbl_i.config(text=f'i: {self.vm.i}')
        self.lbl_s.config(text=f's: {self.vm.s}')

        # atualizar memória/pilha (mostra endereços usados ordenados)
        self.lst_mem.delete(0, tk.END)
        keys = sorted(self.vm.M.keys())
        for k in keys:
            prefix = '<- TOP' if k == self.vm.s else ''
            self.lst_mem.insert(tk.END, f'M[{k}] = {self.vm.M[k]} {prefix}')

    def _periodic_update(self):
        # atualiza indicadores (por exemplo, se VM estiver aguardando input)
        if self.program_loaded and self.vm.waiting_for_input:
            self.lbl_status.config(text='Aguardando RD (forneça input)')
        self.update_gui()
        self.root.after(200, self._periodic_update)
    
    def choose_and_compile(self):
    # abre diálogo para selecionar arquivo .txt e inicia compilação em thread
        path = filedialog.askopenfilename(filetypes=[('Text files', '*.txt'),('All files','*.*')])
        if not path:
            return
        self.entry_input_file = path  # opcional: guarda
        # executa em thread para não travar a GUI
        t = threading.Thread(target=self._run_compile_and_load, args=(path,), daemon=True)
        t.start()

    def _run_compile_and_load(self, txt_path):
        self.lbl_status.config(text='Compilando...')
        try:
                # chama o compilador como subprocesso externo
                # ajusta: COMPILER_SCRIPT deve ser o script que inicia seu compilador
                cmd = [os.environ.get("PYTHON", "python"), COMPILER_SCRIPT, txt_path]
                # você pode querer passar argumento extra para o compilador; ajuste se necessário
                proc = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())

                stdout = proc.stdout or ""
                stderr = proc.stderr or ""

                base = os.path.splitext(os.path.basename(txt_path))[0]
                expected_obj = base + ".obj"
                obj_src = os.path.join(os.getcwd(), expected_obj)

                if proc.returncode != 0:
                    # compilador falhou — mostra saída e erro
                    msg = f"Compilador retornou código {proc.returncode}\n\nstdout:\n{stdout}\nstderr:\n{stderr}"
                    messagebox.showerror("Erro compilação", msg)
                    self.lbl_status.config(text='Erro na compilação')
                    return

                # tenta localizar o .obj — primeiro na raiz, senão procura em algumas pastas comuns
                possible_paths = [obj_src,
                                os.path.join(os.getcwd(), "outputs", expected_obj),
                                os.path.join(os.getcwd(), "src", expected_obj)]

                found = None
                for p in possible_paths:
                    if os.path.isfile(p):
                        found = p
                        break

                if not found:
                    # não encontrou: mostra aviso com stdout/stderr
                    msg = "Compilação concluída, mas .obj não foi encontrado.\n\n"
                    msg += f"Procurado em:\n{possible_paths}\n\nstdout:\n{stdout}\n\nstderr:\n{stderr}"
                    messagebox.showwarning("Aviso", msg)
                    self.lbl_status.config(text='Compilação: obj não encontrado')
                    return

                # move para outputs (sobrescreve se já existir)
                dst = os.path.join(OUTPUTS_DIR, expected_obj)
                try:
                    if os.path.abspath(found) != os.path.abspath(dst):
                        shutil.move(found, dst)
                    else:
                        # já está no lugar
                        pass
                except Exception as e:
                    messagebox.showwarning("Aviso", f"Falha ao mover .obj para outputs: {e}\nUsando arquivo original.")
                    dst = found

                # agora carregamos o .obj na VM
                try:
                    with open(dst, 'r', encoding='utf-8') as f:
                        text = f.read()
                    program = parse_obj_text(text)
                    self.vm = MVDMachine(program)
                    self.program_loaded = True
                    self.update_gui()
                    self.lbl_status.config(text=f'Carregado: {os.path.basename(dst)}')
                    messagebox.showinfo("OK", f".obj carregado na VM: {dst}")
                except Exception as e:
                    messagebox.showerror("Erro ao carregar .obj", str(e))
                    self.lbl_status.config(text='Erro ao carregar .obj')
                    return
        except Exception as e:
            messagebox.showerror("Erro ao iniciar o Compilador", str(e))

        

            

# -----------------------------
# main
# -----------------------------

def main():
    root = tk.Tk()
    app = MVDGUI(root)
    root.geometry('900x600')
    root.mainloop()

if __name__ == '__main__':
    main()
