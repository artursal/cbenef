import json
import re
import roman
from thefuzz import fuzz

class CbenefEngine:
    def __init__(self, db_path='cbenef_db.json'):
        with open(db_path, 'r', encoding='utf-8') as f:
            self.db = json.load(f)
        
    def normalize_text(self, text):
        if not text:
            return ""
        text = text.lower()
        # Normalize common abbreviations
        text = re.sub(r'artigo\s*', 'art ', text)
        text = re.sub(r'art\.\s*', 'art ', text)
        text = re.sub(r'anexo\s*', 'anx ', text)
        text = re.sub(r'parágrafo\s*', 'par ', text)
        text = re.sub(r'inciso\s*', 'inc ', text)
        
        # Convert roman numerals to integers for consistent matching
        # Find roman numerals at the end of word boundaries
        def roman_to_int(match):
            r = match.group(0).upper()
            try:
                return str(roman.fromRoman(r))
            except:
                return r
        
        # Look for anx I, anx II, etc
        text = re.sub(r'(?<=anx\s)([ivxlcdm]+)\b', roman_to_int, text)
        # Look for anx 1, anx 2, etc (normalize leading zeros)
        text = re.sub(r'\b0+(\d+)', r'\1', text)
        
        return text.strip()

    def extract_key_identifiers(self, text):
        norm = self.normalize_text(text)
        # Try to extract numbers associated with art and anx
        art_match = re.search(r'art\s+(\d+)', norm)
        anx_match = re.search(r'anx\s+(\d+)', norm)
        
        return {
            "art": art_match.group(1) if art_match else None,
            "anx": anx_match.group(1) if anx_match else None,
            "full_norm": norm
        }

    def suggest(self, cst, legal_text, ncm=None, cfop=None):
        cst = str(cst).zfill(2)
        input_keys = self.extract_key_identifiers(legal_text)
        
        # Regra Injetada: Diferimento/Industrializacao por CFOP (SP054020 sem NCM atrelado na base)
        if cst == '50' and cfop and cfop.startswith(('5901', '6901', '5902', '6902', '5903', '6903', '5924', '6924')):
            return {"code": "SP054020", "confidence": 1.0, "message": "Retorno de Industrialização identificado via CFOP."}
        
        # 1. Filter by CST candidates
        candidates = [e for e in self.db if cst in e.get('csts', [])]
        
        if not candidates:
            if cst in ['00', '10', '60', '02', '15', '61']:
                return {"code": None, "confidence": 1.0, "message": "CST não requer cBenef em SP."}
            return {"code": "SEM CBENEF", "confidence": 0.8, "message": "CST requer cBenef mas nenhum código de benefício específico foi encontrado."}

        scored_candidates = []
        for cand in candidates:
            score = 0
            cand_keys = self.extract_key_identifiers(cand.get('norm_dispositivo', ''))
            
            # Match Article and Annex exactly (highest weight)
            if input_keys['art'] and cand_keys['art'] == input_keys['art']:
                score += 50
            if input_keys['anx'] and cand_keys['anx'] == input_keys['anx']:
                score += 30
            
            # Fuzzy match on description
            fuzzy_score = fuzz.token_set_ratio(input_keys['full_norm'], cand.get('norm_descricao', ''))
            score += (fuzzy_score * 0.2) # Max 20 points
            
            # Match NCM
            if ncm and ncm in cand.get('ncms', []):
                score += 60 # Highest confidence if exact NCM from SEFAZ table
            
            scored_candidates.append((score, cand))
        
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        
        if scored_candidates:
            best_score, best_cand = scored_candidates[0]
            
            if best_score >= 50: # At least article matched or NCM
                return {
                    "code": best_cand['code'],
                    "confidence": min(1.0, best_score / 100.0),
                    "match_type": "rule_based",
                    "description": best_cand.get('norm_descricao', ''),
                    "dispositivo": best_cand.get('norm_dispositivo', '')
                }
            elif best_score > 15: # Only fuzzy or partial match
                return {
                    "code": best_cand['code'],
                    "confidence": best_score / 100.0,
                    "match_type": "fuzzy",
                    "description": best_cand.get('norm_descricao', '')
                }

        # 4. Fallback: SEM CBENEF
        return {
            "code": "SEM CBENEF", 
            "confidence": 0.5, 
            "message": "Nenhum benefício específico identificado com segurança. Utilize 'SEM CBENEF'."
        }

if __name__ == "__main__":
    engine = CbenefEngine()
    
    test_cases = [
        {"cst": "40", "text": "Isenção conf. Artigo 14 do Anexo I"},
        {"cst": "20", "text": "Redução Base de Cálculo Art. 1 do Anexo II"},
        {"cst": "40", "text": "Isento conforme Artigo 18 do Anexo I do RICMS/00"},
        {"cst": "90", "text": "Processo Judicial nr 12345"},
    ]
    
    print(f"{'CST':<5} | {'Input Text':<45} | {'Code':<10} | {'Conf':<5} | {'Reason'}")
    print("-" * 100)
    for tc in test_cases:
        res = engine.suggest(tc['cst'], tc['text'])
        print(f"{tc['cst']:<5} | {tc['text']:<45} | {str(res['code']):<10} | {res.get('confidence', 0):.2f} | {res.get('match_type') or res.get('message')}")
