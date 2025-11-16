# Provider Auto Discovery Report

**Generated:** 2025-11-16 14:26:00

## Summary

- **Files Scanned:** 7
- **Candidate Providers Discovered:** 49
- **Duplicates Skipped:** 112
- **Valid Providers:** 5
- **Invalid Providers:** 44
- **Providers Added to Config:** 5

## Valid Providers

These providers passed validation and were added to the configuration:

| Provider ID | Name | Category | Base URL | Response Time (ms) |
|------------|------|----------|----------|-------------------|
| `blockscout` | Blockscout Ethereum | blockchain_explorers | https://eth.blockscout.com/api | 143.81 |
| `blockscout_ethereum` | Blockscout Ethereum | blockchain_explorers | https://eth.blockscout.com/api | 137.02 |
| `bscscan_primary` | BscScan | blockchain_explorers | https://api.bscscan.com/api | 187.79 |
| `etherscan_primary` | Etherscan | blockchain_explorers | https://api.etherscan.io/api | 42.48 |
| `etherscan_secondary` | Etherscan (secondary key) | blockchain_explorers | https://api.etherscan.io/api | 177.30 |

## Invalid Providers

These providers failed validation and were NOT added:

| Provider ID | Name | Category | Base URL | Error |
|------------|------|----------|----------|-------|
| `alchemy_eth` | Alchemy Ethereum Mainnet | rpc | https://eth-mainnet.g.alchemy.com/v2 | No testable endpoints found |
| `alchemy_eth_mainnet` | Alchemy Ethereum Mainnet | rpc | https://eth-mainnet.g.alchemy.com/v2/{API_KEY} | No testable endpoints found |
| `alchemy_eth_mainnet_ws` | Alchemy Ethereum Mainnet WS | blockchain_explorers | wss://eth-mainnet.g.alchemy.com/v2/{API_KEY} | No testable endpoints found |
| `ankr_bsc` | Ankr BSC | rpc | https://rpc.ankr.com/bsc | No testable endpoints found |
| `ankr_eth` | Ankr Ethereum | rpc | https://rpc.ankr.com/eth | No testable endpoints found |
| `ankr_multichain_bsc` | Ankr MultiChain (BSC) | blockchain_explorers | https://rpc.ankr.com/multichain | HTTP 404: <html>
<head><title>404 Not Found</title></head>
<body>
<center><h1>404 Not Found</h1><... |
| `ankr_polygon` | Ankr Polygon | rpc | https://rpc.ankr.com/polygon | No testable endpoints found |
| `bitquery_bsc` | BitQuery (BSC) | blockchain_explorers | https://graphql.bitquery.io | Authentication required (HTTP 401) |
| `blockchair_ethereum` | Blockchair Ethereum | blockchain_explorers | https://api.blockchair.com/ethereum | HTTP 402: {"data":null,"context":{"code":402,"error":"Invalid API token. Please contact us at info@b... |
| `blockchair_tron` | Blockchair TRON | blockchain_explorers | https://api.blockchair.com/tron | HTTP 402: {"data":null,"context":{"code":402,"error":"Invalid API token. Please contact us at info@b... |
| `bsc_official_alt1` | BSC Official Alt1 | rpc | https://bsc-dataseed1.defibit.io | No testable endpoints found |
| `bsc_official_alt2` | BSC Official Alt2 | rpc | https://bsc-dataseed1.ninicoin.io | No testable endpoints found |
| `bsc_official_mainnet` | BSC Official Mainnet | rpc | https://bsc-dataseed.binance.org | No testable endpoints found |
| `bsctrace` | BscTrace | blockchain_explorers | https://api.bsctrace.com | No testable endpoints found |
| `chainlens` | Chainlens | blockchain_explorers | https://api.chainlens.com | No testable endpoints found |
| `cloudflare_eth` | Cloudflare Ethereum | rpc | https://cloudflare-eth.com | No testable endpoints found |
| `coinmarketcap` | CoinMarketCap | market_data | https://pro-api.coinmarketcap.com/v1 | Authentication required (HTTP 401) |
| `drpc_eth` | dRPC Ethereum | rpc | https://eth.drpc.org | No testable endpoints found |
| `etherchain` | Etherchain | blockchain_explorers | https://www.etherchain.org/api | No testable endpoints found |
| `getblock_tron` | GetBlock TRON | blockchain_explorers | https://go.getblock.io/tron | No testable endpoints found |
| `huggingface_cryptobert` | HuggingFace CryptoBERT | ml_model | https://api-inference.huggingface.co/models/ElKulako/cryptobert | No testable endpoints found |
| `infura_eth` | Infura Ethereum Mainnet | rpc | https://mainnet.infura.io/v3 | No testable endpoints found |
| `infura_eth_mainnet` | Infura Ethereum Mainnet | rpc | https://mainnet.infura.io/v3/{PROJECT_ID} | No testable endpoints found |
| `infura_eth_sepolia` | Infura Ethereum Sepolia | rpc | https://sepolia.infura.io/v3/{PROJECT_ID} | No testable endpoints found |
| `llamanodes_eth` | LlamaNodes Ethereum | rpc | https://eth.llamarpc.com | No testable endpoints found |
| `nodereal_bsc` | Nodereal BSC | rpc | https://bsc-mainnet.nodereal.io/v1/{API_KEY} | No testable endpoints found |
| `nodereal_bsc_explorer` | Nodereal BSC | blockchain_explorers | https://bsc-mainnet.nodereal.io/v1/{API_KEY} | No testable endpoints found |
| `one_rpc_eth` | 1RPC Ethereum | rpc | https://1rpc.io/eth | No testable endpoints found |
| `oneinch_bsc_api` | 1inch BSC API | blockchain_explorers | https://api.1inch.io/v5.0/56 | No testable endpoints found |
| `polygon_mumbai` | Polygon Mumbai | rpc | https://rpc-mumbai.maticvigil.com | No testable endpoints found |
| `polygon_official_mainnet` | Polygon Official Mainnet | rpc | https://polygon-rpc.com | No testable endpoints found |
| `publicnode_bsc` | PublicNode BSC | rpc | https://bsc-rpc.publicnode.com | No testable endpoints found |
| `publicnode_eth` | PublicNode Ethereum | rpc | https://ethereum.publicnode.com | No testable endpoints found |
| `publicnode_eth_allinone` | PublicNode Ethereum All-in-one | rpc | https://ethereum-rpc.publicnode.com | No testable endpoints found |
| `publicnode_eth_mainnet` | PublicNode Ethereum | rpc | https://ethereum.publicnode.com | No testable endpoints found |
| `publicnode_polygon_bor` | PublicNode Polygon Bor | rpc | https://polygon-bor-rpc.publicnode.com | No testable endpoints found |
| `tron_nile_testnet` | Tron Nile Testnet | rpc | https://api.nileex.io | No testable endpoints found |
| `trongrid_explorer` | TronGrid (Official) | blockchain_explorers | https://api.trongrid.io | HTTP 404: {"Success":false,"Error":"TronGrid service does not support this API.","StatusCode":404}
 |
| `trongrid_mainnet` | TronGrid Mainnet | rpc | https://api.trongrid.io | No testable endpoints found |
| `tronscan` | TronScan | blockchain_explorers | https://apilist.tronscanapi.com/api | HTTP 400: {"message":"some parameters are invalid or out of range"}
 |
| `tronscan_api_v2` | Tronscan API v2 | blockchain_explorers | https://api.tronscan.org/api | No testable endpoints found |
| `tronscan_primary` | TronScan | blockchain_explorers | https://apilist.tronscanapi.com/api | HTTP 400: {"message":"some parameters are invalid or out of range"}
 |
| `tronstack_mainnet` | TronStack Mainnet | rpc | https://api.tronstack.io | No testable endpoints found |
| `whale_alert` | Whale Alert | whale_tracking | https://api.whale-alert.io/v1 | Authentication required (HTTP 401) |

## Integration Notes

- **Config File Updated:** `providers_config_extended.json`
- **Backup Created:** `providers_config_extended.json.backup_*`

### Pool Assignments

- **Blockchain Explorer Pool** (blockchain_explorers): 10 total providers, 5 new

## Detailed Validation Results

### `alchemy_eth`

- **Name:** Alchemy Ethereum Mainnet
- **Category:** rpc
- **Base URL:** https://eth-mainnet.g.alchemy.com/v2
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** providers_config_ultimate.json

### `alchemy_eth_mainnet`

- **Name:** Alchemy Ethereum Mainnet
- **Category:** rpc
- **Base URL:** https://eth-mainnet.g.alchemy.com/v2/{API_KEY}
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `alchemy_eth_mainnet_ws`

- **Name:** Alchemy Ethereum Mainnet WS
- **Category:** blockchain_explorers
- **Base URL:** wss://eth-mainnet.g.alchemy.com/v2/{API_KEY}
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `ankr_bsc`

- **Name:** Ankr BSC
- **Category:** rpc
- **Base URL:** https://rpc.ankr.com/bsc
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `ankr_eth`

- **Name:** Ankr Ethereum
- **Category:** rpc
- **Base URL:** https://rpc.ankr.com/eth
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `ankr_multichain_bsc`

- **Name:** Ankr MultiChain (BSC)
- **Category:** blockchain_explorers
- **Base URL:** https://rpc.ankr.com/multichain
- **Status:** invalid
- **HTTP Status:** 404
- **Response Time:** 92.73ms
- **Test Endpoint:** `https://rpc.ankr.com/multichain/POST with JSON-RPC body`
- **Error:** HTTP 404: <html>
<head><title>404 Not Found</title></head>
<body>
<center><h1>404 Not Found</h1></center>
<hr><center>nginx</center>
</body>
</html>

- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `ankr_polygon`

- **Name:** Ankr Polygon
- **Category:** rpc
- **Base URL:** https://rpc.ankr.com/polygon
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `bitquery_bsc`

- **Name:** BitQuery (BSC)
- **Category:** blockchain_explorers
- **Base URL:** https://graphql.bitquery.io
- **Status:** requires_auth
- **HTTP Status:** 401
- **Response Time:** 439.10ms
- **Test Endpoint:** `https://graphql.bitquery.io/POST with body: { query: '{ ethereum(network: bsc) { address(address: {is: "0x0000000000000000000000000000000000000000"}) { balances { currency { symbol } value } } } }' }`
- **Error:** Authentication required (HTTP 401)
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `blockchair_ethereum`

- **Name:** Blockchair Ethereum
- **Category:** blockchain_explorers
- **Base URL:** https://api.blockchair.com/ethereum
- **Status:** invalid
- **HTTP Status:** 402
- **Response Time:** 542.44ms
- **Test Endpoint:** `https://api.blockchair.com/ethereum/dashboards/address/0x0000000000000000000000000000000000000000?key={key}`
- **Error:** HTTP 402: {"data":null,"context":{"code":402,"error":"Invalid API token. Please contact us at info@blockchair.com.","market_price_usd":3150.47,"cache":{"live":true,"duration":180,"since":"2025-11-16 14:26:00","
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `blockchair_tron`

- **Name:** Blockchair TRON
- **Category:** blockchain_explorers
- **Base URL:** https://api.blockchair.com/tron
- **Status:** invalid
- **HTTP Status:** 402
- **Response Time:** 546.80ms
- **Test Endpoint:** `https://api.blockchair.com/tron/dashboards/address/0x0000000000000000000000000000000000000000?key={key}`
- **Error:** HTTP 402: {"data":null,"context":{"code":402,"error":"Invalid API token. Please contact us at info@blockchair.com.","cache":{"live":true,"duration":120,"since":"2025-11-16 14:26:00","until":"2025-11-16 14:28:00
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `blockscout`

- **Name:** Blockscout Ethereum
- **Category:** blockchain_explorers
- **Base URL:** https://eth.blockscout.com/api
- **Status:** valid
- **HTTP Status:** 200
- **Response Time:** 143.81ms
- **Test Endpoint:** `https://eth.blockscout.com/api/?module=account&action=balance&address=0x0000000000000000000000000000000000000000`
- **Response Sample:** {'preview': "{'message': 'OK', 'result': '14133068689633800659882', 'status': '1'}"}
- **Source File:** providers_config_ultimate.json

### `blockscout_ethereum`

- **Name:** Blockscout Ethereum
- **Category:** blockchain_explorers
- **Base URL:** https://eth.blockscout.com/api
- **Status:** valid
- **HTTP Status:** 200
- **Response Time:** 137.02ms
- **Test Endpoint:** `https://eth.blockscout.com/api/?module=account&action=balance&address=0x0000000000000000000000000000000000000000`
- **Response Sample:** {'preview': "{'message': 'OK', 'result': '14133068689633800659882', 'status': '1'}"}
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `bsc_official_alt1`

- **Name:** BSC Official Alt1
- **Category:** rpc
- **Base URL:** https://bsc-dataseed1.defibit.io
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `bsc_official_alt2`

- **Name:** BSC Official Alt2
- **Category:** rpc
- **Base URL:** https://bsc-dataseed1.ninicoin.io
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `bsc_official_mainnet`

- **Name:** BSC Official Mainnet
- **Category:** rpc
- **Base URL:** https://bsc-dataseed.binance.org
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `bscscan_primary`

- **Name:** BscScan
- **Category:** blockchain_explorers
- **Base URL:** https://api.bscscan.com/api
- **Status:** valid
- **HTTP Status:** 200
- **Response Time:** 187.79ms
- **Test Endpoint:** `https://api.bscscan.com/api/?module=account&action=balance&address=0x0000000000000000000000000000000000000000&apikey={key}`
- **Response Sample:** {'preview': "{'status': '0', 'message': 'NOTOK', 'result': 'You are using a deprecated V1 endpoint, switch to Etherscan API V2 using https://docs.etherscan.io/v2-migration'}"}
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `bsctrace`

- **Name:** BscTrace
- **Category:** blockchain_explorers
- **Base URL:** https://api.bsctrace.com
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `chainlens`

- **Name:** Chainlens
- **Category:** blockchain_explorers
- **Base URL:** https://api.chainlens.com
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `cloudflare_eth`

- **Name:** Cloudflare Ethereum
- **Category:** rpc
- **Base URL:** https://cloudflare-eth.com
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `coinmarketcap`

- **Name:** CoinMarketCap
- **Category:** market_data
- **Base URL:** https://pro-api.coinmarketcap.com/v1
- **Status:** requires_auth
- **HTTP Status:** 401
- **Response Time:** 48.39ms
- **Test Endpoint:** `https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol=BTCUSDT&apikey=04cf4b5b-9868-465c-8ba0-9f2e78c92eb1`
- **Error:** Authentication required (HTTP 401)
- **Source File:** providers_config_ultimate.json

### `drpc_eth`

- **Name:** dRPC Ethereum
- **Category:** rpc
- **Base URL:** https://eth.drpc.org
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `etherchain`

- **Name:** Etherchain
- **Category:** blockchain_explorers
- **Base URL:** https://www.etherchain.org/api
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `etherscan_primary`

- **Name:** Etherscan
- **Category:** blockchain_explorers
- **Base URL:** https://api.etherscan.io/api
- **Status:** valid
- **HTTP Status:** 200
- **Response Time:** 42.48ms
- **Test Endpoint:** `https://api.etherscan.io/api/?module=account&action=balance&address=0x0000000000000000000000000000000000000000&tag=latest&apikey={key}`
- **Response Sample:** {'preview': "{'status': '0', 'message': 'NOTOK', 'result': 'You are using a deprecated V1 endpoint, switch to Etherscan API V2 using https://docs.etherscan.io/v2-migration'}"}
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `etherscan_secondary`

- **Name:** Etherscan (secondary key)
- **Category:** blockchain_explorers
- **Base URL:** https://api.etherscan.io/api
- **Status:** valid
- **HTTP Status:** 200
- **Response Time:** 177.30ms
- **Test Endpoint:** `https://api.etherscan.io/api/?module=account&action=balance&address=0x0000000000000000000000000000000000000000&tag=latest&apikey={key}`
- **Response Sample:** {'preview': "{'status': '0', 'message': 'NOTOK', 'result': 'You are using a deprecated V1 endpoint, switch to Etherscan API V2 using https://docs.etherscan.io/v2-migration'}"}
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `getblock_tron`

- **Name:** GetBlock TRON
- **Category:** blockchain_explorers
- **Base URL:** https://go.getblock.io/tron
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `huggingface_cryptobert`

- **Name:** HuggingFace CryptoBERT
- **Category:** ml_model
- **Base URL:** https://api-inference.huggingface.co/models/ElKulako/cryptobert
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** providers_config_ultimate.json

### `infura_eth`

- **Name:** Infura Ethereum Mainnet
- **Category:** rpc
- **Base URL:** https://mainnet.infura.io/v3
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** providers_config_ultimate.json

### `infura_eth_mainnet`

- **Name:** Infura Ethereum Mainnet
- **Category:** rpc
- **Base URL:** https://mainnet.infura.io/v3/{PROJECT_ID}
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `infura_eth_sepolia`

- **Name:** Infura Ethereum Sepolia
- **Category:** rpc
- **Base URL:** https://sepolia.infura.io/v3/{PROJECT_ID}
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `llamanodes_eth`

- **Name:** LlamaNodes Ethereum
- **Category:** rpc
- **Base URL:** https://eth.llamarpc.com
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `nodereal_bsc`

- **Name:** Nodereal BSC
- **Category:** rpc
- **Base URL:** https://bsc-mainnet.nodereal.io/v1/{API_KEY}
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `nodereal_bsc_explorer`

- **Name:** Nodereal BSC
- **Category:** blockchain_explorers
- **Base URL:** https://bsc-mainnet.nodereal.io/v1/{API_KEY}
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `one_rpc_eth`

- **Name:** 1RPC Ethereum
- **Category:** rpc
- **Base URL:** https://1rpc.io/eth
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `oneinch_bsc_api`

- **Name:** 1inch BSC API
- **Category:** blockchain_explorers
- **Base URL:** https://api.1inch.io/v5.0/56
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `polygon_mumbai`

- **Name:** Polygon Mumbai
- **Category:** rpc
- **Base URL:** https://rpc-mumbai.maticvigil.com
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `polygon_official_mainnet`

- **Name:** Polygon Official Mainnet
- **Category:** rpc
- **Base URL:** https://polygon-rpc.com
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `publicnode_bsc`

- **Name:** PublicNode BSC
- **Category:** rpc
- **Base URL:** https://bsc-rpc.publicnode.com
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `publicnode_eth`

- **Name:** PublicNode Ethereum
- **Category:** rpc
- **Base URL:** https://ethereum.publicnode.com
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** providers_config_ultimate.json

### `publicnode_eth_allinone`

- **Name:** PublicNode Ethereum All-in-one
- **Category:** rpc
- **Base URL:** https://ethereum-rpc.publicnode.com
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `publicnode_eth_mainnet`

- **Name:** PublicNode Ethereum
- **Category:** rpc
- **Base URL:** https://ethereum.publicnode.com
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `publicnode_polygon_bor`

- **Name:** PublicNode Polygon Bor
- **Category:** rpc
- **Base URL:** https://polygon-bor-rpc.publicnode.com
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `tron_nile_testnet`

- **Name:** Tron Nile Testnet
- **Category:** rpc
- **Base URL:** https://api.nileex.io
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `trongrid_explorer`

- **Name:** TronGrid (Official)
- **Category:** blockchain_explorers
- **Base URL:** https://api.trongrid.io
- **Status:** invalid
- **HTTP Status:** 404
- **Response Time:** 252.60ms
- **Test Endpoint:** `https://api.trongrid.io/POST /wallet/getaccount with body: { "address": "0x0000000000000000000000000000000000000000", "visible": true }`
- **Error:** HTTP 404: {"Success":false,"Error":"TronGrid service does not support this API.","StatusCode":404}

- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `trongrid_mainnet`

- **Name:** TronGrid Mainnet
- **Category:** rpc
- **Base URL:** https://api.trongrid.io
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `tronscan`

- **Name:** TronScan
- **Category:** blockchain_explorers
- **Base URL:** https://apilist.tronscanapi.com/api
- **Status:** invalid
- **HTTP Status:** 400
- **Response Time:** 64.57ms
- **Test Endpoint:** `https://apilist.tronscanapi.com/api/account?address=0x0000000000000000000000000000000000000000&apikey=7ae72726-bffe-4e74-9c33-97b761eeea21`
- **Error:** HTTP 400: {"message":"some parameters are invalid or out of range"}

- **Source File:** providers_config_ultimate.json

### `tronscan_api_v2`

- **Name:** Tronscan API v2
- **Category:** blockchain_explorers
- **Base URL:** https://api.tronscan.org/api
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `tronscan_primary`

- **Name:** TronScan
- **Category:** blockchain_explorers
- **Base URL:** https://apilist.tronscanapi.com/api
- **Status:** invalid
- **HTTP Status:** 400
- **Response Time:** 13.17ms
- **Test Endpoint:** `https://apilist.tronscanapi.com/api/account?address=0x0000000000000000000000000000000000000000`
- **Error:** HTTP 400: {"message":"some parameters are invalid or out of range"}

- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `tronstack_mainnet`

- **Name:** TronStack Mainnet
- **Category:** rpc
- **Base URL:** https://api.tronstack.io
- **Status:** invalid
- **HTTP Status:** N/A
- **Response Time:** N/A
- **Test Endpoint:** `None`
- **Error:** No testable endpoints found
- **Source File:** api-resources/crypto_resources_unified_2025-11-11.json

### `whale_alert`

- **Name:** Whale Alert
- **Category:** whale_tracking
- **Base URL:** https://api.whale-alert.io/v1
- **Status:** requires_auth
- **HTTP Status:** 401
- **Response Time:** 94.83ms
- **Test Endpoint:** `https://api.whale-alert.io/v1/transactions?api_key={key}&min_value=1000000&start={ts}&end={ts}`
- **Error:** Authentication required (HTTP 401)
- **Source File:** providers_config_ultimate.json
