# -*- coding: utf-8 -*-
#!/usr/bin/env python3

from copy import deepcopy
from decimal import Decimal
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

MAX_TX = 999

NS_SEPA = "urn:iso:std:iso:20022:tech:xsd:pain.008.001.02"
NS_XSI = "http://www.w3.org/2001/XMLSchema-instance"

NS = {"sepa": NS_SEPA}

ET.register_namespace("", NS_SEPA)
ET.register_namespace("xsi", NS_XSI)


def get_text(parent, path):
    el = parent.find(path, NS)
    return el.text if el is not None else None


def set_text(parent, path, value):
    el = parent.find(path, NS)
    if el is not None:
        el.text = str(value)


def make_id(old_id, part_no):
    """
    SEPA-IDs wie MsgId und PmtInfId duerfen oft max. 35 Zeichen haben.
    Daher kuerzen wir sauber und haengen eine eindeutige Teilnummer an.
    """
    suffix = f"-S{part_no:03d}"
    if not old_id:
        return f"SPLIT{suffix}"

    max_base_len = 35 - len(suffix)
    return old_id[:max_base_len] + suffix


def tx_amount(tx):
    amt = tx.find(".//sepa:InstdAmt", NS)
    if amt is None or amt.text is None:
        raise ValueError("Betrag InstdAmt nicht gefunden")
    return Decimal(amt.text.replace(",", "."))


def split_sepa(input_file):
    input_path = Path(input_file)

    tree = ET.parse(input_path)
    root = tree.getroot()

    initn = root.find("sepa:CstmrDrctDbtInitn", NS)
    if initn is None:
        raise ValueError("CstmrDrctDbtInitn nicht gefunden")

    pmt_infs = initn.findall("sepa:PmtInf", NS)
    if not pmt_infs:
        raise ValueError("Keine PmtInf-Bloecke gefunden")

    part_no = 1

    for pmt_inf in pmt_infs:
        txs = pmt_inf.findall("sepa:DrctDbtTxInf", NS)

        if not txs:
            continue

        for start in range(0, len(txs), MAX_TX):
            chunk = txs[start:start + MAX_TX]

            new_root = deepcopy(root)
            new_initn = new_root.find("sepa:CstmrDrctDbtInitn", NS)
            new_grp_hdr = new_initn.find("sepa:GrpHdr", NS)

            # Alle PmtInf-Bloecke entfernen
            for existing_pmt in list(new_initn.findall("sepa:PmtInf", NS)):
                new_initn.remove(existing_pmt)

            # Aktuellen PmtInf-Block kopieren
            new_pmt_inf = deepcopy(pmt_inf)

            # Alte Transaktionen entfernen
            for old_tx in list(new_pmt_inf.findall("sepa:DrctDbtTxInf", NS)):
                new_pmt_inf.remove(old_tx)

            # Teilmenge einfuegen
            for tx in chunk:
                new_pmt_inf.append(deepcopy(tx))

            count = len(chunk)
            total = sum(tx_amount(tx) for tx in chunk)
            total_str = f"{total:.2f}"

            # GrpHdr aktualisieren
            set_text(new_grp_hdr, "sepa:NbOfTxs", count)
            set_text(new_grp_hdr, "sepa:CtrlSum", total_str)

            old_msg_id = get_text(new_grp_hdr, "sepa:MsgId")
            set_text(new_grp_hdr, "sepa:MsgId", make_id(old_msg_id, part_no))

            # PmtInf aktualisieren
            set_text(new_pmt_inf, "sepa:NbOfTxs", count)
            set_text(new_pmt_inf, "sepa:CtrlSum", total_str)

            old_pmt_id = get_text(new_pmt_inf, "sepa:PmtInfId")
            set_text(new_pmt_inf, "sepa:PmtInfId", make_id(old_pmt_id, part_no))

            new_initn.append(new_pmt_inf)

            output_file = input_path.with_name(
                f"{input_path.stem}_teil_{part_no:03d}{input_path.suffix}"
            )

            ET.ElementTree(new_root).write(
                output_file,
                encoding="UTF-8",
                xml_declaration=True,
                short_empty_elements=False
            )

            print(
                f"Erzeugt: {output_file.name} | "
                f"Buchungen: {count} | "
                f"Summe: {total_str} | "
                f"MsgId: {make_id(old_msg_id, part_no)} | "
                f"PmtInfId: {make_id(old_pmt_id, part_no)}"
            )

            part_no += 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Aufruf: py sepa_split.py datei.xml")
        sys.exit(1)

    split_sepa(sys.argv[1])