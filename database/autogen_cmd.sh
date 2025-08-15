#!/bin/bash
set -e  # stop on error

# Colors
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
CYAN="\033[0;36m"
NC="\033[0m" # No Color

log() {
    echo -e "${CYAN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $*"
}

success() {
    echo -e "${GREEN}[DONE]${NC} $*"
}

error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

log "${YELLOW}=== Starting S57 metadata generation ===${NC}"

log "Processing ANTHOI"
python ./s57_metadata_gen.py -s 20250622/ENC_VN_2023/ANTHOI_db/ENC_ROOT/V25AT001.000 -o ENC_VN_2023/ANTHOI && success "ANTHOI" || { error "ANTHOI failed"; exit 1; }

log "Processing BANGOI"
python ./s57_metadata_gen.py -s 20250622/ENC_VN_2023/BANGOI_db/ENC_ROOT/V24BN001.000 -o ENC_VN_2023/BANGOI && success "BANGOI" || { error "BANGOI failed"; exit 1; }

log "Processing BINHTRI"
python ./s57_metadata_gen.py -s 20250622/ENC_VN_2023/BINHTRI_db/ENC_ROOT/V24BT001.000 -o ENC_VN_2023/BINHTRI && success "BINHTRI" || { error "BINHTRI failed"; exit 1; }

log "Processing CONDAO"
python ./s57_metadata_gen.py -s 20250622/ENC_VN_2023/CONDAO_db/ENC_ROOT/V24CD001.000 -o ENC_VN_2023/CONDAO && success "CONDAO" || { error "CONDAO failed"; exit 1; }

log "Processing DAMMON"
python ./s57_metadata_gen.py -s 20250622/ENC_VN_2023/DAMMON_db/ENC_ROOT/V24DM001.000 -o ENC_VN_2023/DAMMON && success "DAMMON" || { error "DAMMON failed"; exit 1; }

log "Processing DONGNAI"
python ./s57_metadata_gen.py -s 20250622/ENC_VN_2023/DONGNAI_db/ENC_ROOT/V24DN001.000 -o ENC_VN_2023/DONGNAI && success "DONGNAI" || { error "DONGNAI failed"; exit 1; }

log "Processing HATIEN"
python ./s57_metadata_gen.py -s 20250622/ENC_VN_2023/HATIEN_db/ENC_ROOT/V24HT001.000 -o ENC_VN_2023/HATIEN && success "HATIEN" || { error "HATIEN failed"; exit 1; }

log "${GREEN}=== All ENC metadata generated successfully ===${NC}"
