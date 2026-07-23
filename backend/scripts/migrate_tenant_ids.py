"""Migracao multitenant Petra Suite — tenant_1 / sem tenant -> itvalley.

Em TODAS as colecoes do database, documentos com tenant_id ausente ou
igual a 'tenant_1' recebem tenant_id='itvalley'.

Uso:
    # dry-run (default): so imprime contagens por colecao
    MONGODB_URI="$(az keyvault secret show --vault-name kv-api-key-itvalley -n mongodb-uri --query value -o tsv)" \
        python scripts/migrate_tenant_ids.py --database flowquote-itvalley

    # aplicar de verdade
    MONGODB_URI=... python scripts/migrate_tenant_ids.py --database flowquote-itvalley --apply

Nunca imprime a URI nem credenciais.
"""
import argparse
import asyncio
import os
import sys

from motor.motor_asyncio import AsyncIOMotorClient

TARGET_TENANT = "itvalley"
FILTER = {"$or": [{"tenant_id": {"$exists": False}}, {"tenant_id": None}, {"tenant_id": "tenant_1"}]}


async def run(database: str, apply: bool) -> None:
    uri = os.environ.get("MONGODB_URI")
    if not uri:
        print("ERRO: defina MONGODB_URI no ambiente (nao passe por argumento).")
        sys.exit(1)

    client = AsyncIOMotorClient(uri)
    db = client[database]
    collections = sorted(await db.list_collection_names())

    mode = "APPLY" if apply else "DRY-RUN"
    print(f"[{mode}] database={database} -> tenant_id='{TARGET_TENANT}'")
    print(f"{'colecao':30} {'total':>8} {'a_migrar':>10} {'migrados':>10}")

    grand_total = grand_todo = grand_done = 0
    for name in collections:
        col = db[name]
        total = await col.count_documents({})
        todo = await col.count_documents(FILTER)
        done = 0
        if apply and todo:
            result = await col.update_many(FILTER, {"$set": {"tenant_id": TARGET_TENANT}})
            done = result.modified_count
        print(f"{name:30} {total:>8} {todo:>10} {done if apply else '-':>10}")
        grand_total += total
        grand_todo += todo
        grand_done += done

    print(f"{'TOTAL':30} {grand_total:>8} {grand_todo:>10} {grand_done if apply else '-':>10}")
    if not apply:
        print("\nNada foi alterado (dry-run). Use --apply para executar.")
    client.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Migra tenant_1/sem tenant -> itvalley")
    parser.add_argument("--database", required=True, help="Nome do database Mongo")
    parser.add_argument("--apply", action="store_true", help="Executa de verdade (default: dry-run)")
    args = parser.parse_args()
    asyncio.run(run(args.database, args.apply))


if __name__ == "__main__":
    main()
