# -*- coding: utf-8 -*-
"""
Client minimal de l'Engine API Qlik Sense (JSON-RPC sur WebSocket).
Cible : Qlik Sense Desktop (moteur local sur ws://localhost:4848).

Usage smoke-test :
    python engine.py            # affiche version moteur + liste des apps
"""
import json
import ssl
from websocket import create_connection

# Endpoints possibles pour Qlik Sense Desktop (on essaie dans l'ordre)
CANDIDATE_URLS = [
    "ws://localhost:4848/app/",
    "ws://localhost:4848/app/engineData",
]

GLOBAL_HANDLE = -1


class QlikEngine:
    def __init__(self, url=None, timeout=30):
        self.url = url
        self.timeout = timeout
        self.ws = None
        self._id = 0

    # --- connexion : essaie les endpoints candidats ---
    def connect(self):
        urls = [self.url] if self.url else CANDIDATE_URLS
        last_err = None
        for u in urls:
            try:
                ws = create_connection(
                    u, timeout=self.timeout,
                    sslopt={"cert_reqs": ssl.CERT_NONE},
                    header=["User-Agent: louvre-builder"],
                )
                self.ws = ws
                self.url = u
                self._drain_async()  # consomme l'eventuel OnConnected
                return self
            except Exception as e:  # noqa
                last_err = e
        raise RuntimeError(f"Connexion moteur impossible. Derniere erreur: {last_err}")

    def _drain_async(self):
        # Lit les messages sans 'id' (notifications) sans bloquer trop longtemps
        self.ws.settimeout(1.5)
        try:
            while True:
                raw = self.ws.recv()
                msg = json.loads(raw)
                if "id" in msg:
                    # remet en file : peu probable ici, on ignore
                    pass
        except Exception:
            pass
        finally:
            self.ws.settimeout(self.timeout)

    def call(self, method, handle=GLOBAL_HANDLE, params=None):
        if params is None:
            params = []
        self._id += 1
        req = {"jsonrpc": "2.0", "id": self._id,
               "handle": handle, "method": method, "params": params}
        self.ws.send(json.dumps(req))
        # lit jusqu'a la reponse avec le bon id (ignore notifications)
        while True:
            raw = self.ws.recv()
            msg = json.loads(raw)
            if msg.get("id") == self._id:
                if "error" in msg:
                    raise RuntimeError(f"{method} -> {msg['error']}")
                return msg.get("result", {})
            # sinon : notification async -> on ignore

    def close(self):
        if self.ws:
            self.ws.close()


def smoke_test():
    eng = QlikEngine().connect()
    print("Connecte sur:", eng.url)
    try:
        ver = eng.call("EngineVersion")
        print("EngineVersion:", json.dumps(ver, ensure_ascii=False))
    except Exception as e:
        print("EngineVersion KO:", e)
    try:
        docs = eng.call("GetDocList")
        lst = docs.get("qDocList", [])
        print(f"Apps existantes ({len(lst)}):")
        for d in lst:
            print("  -", d.get("qDocName"), "|", d.get("qDocId"))
    except Exception as e:
        print("GetDocList KO:", e)
    eng.close()


if __name__ == "__main__":
    smoke_test()
