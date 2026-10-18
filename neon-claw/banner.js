/**
 * NemoClaw Claude-Code Style Terminal Banner for Node.js
 */

function printBanner(nodeRole = "Home Server Gateway", extraDetail = "") {
    const RESET = "\x1b[0m";
    const BOLD = "\x1b[1m";
    const DIM = "\x1b[2m";
    const CYAN = "\x1b[36m";
    const BRIGHT_CYAN = "\x1b[96m";
    const PURPLE = "\x1b[35m";
    const BRIGHT_PURPLE = "\x1b[95m";
    const GREEN = "\x1b[32m";
    const BRIGHT_GREEN = "\x1b[92m";
    const YELLOW = "\x1b[33m";
    const GRAY = "\x1b[90m";

    const banner = `
${BRIGHT_PURPLE}  ╭──────────────────────────────────────────────────────────────────────────╮${RESET}
${BRIGHT_PURPLE}  │${RESET}                                                                          ${BRIGHT_PURPLE}│${RESET}
${BRIGHT_PURPLE}  │${RESET}   ${BOLD}${BRIGHT_CYAN}✦  N E M O C L A W${RESET}  ${DIM}v1.0.0${RESET}                                       ${BRIGHT_PURPLE}│${RESET}
${BRIGHT_PURPLE}  │${RESET}      ${DIM}Personal AI Agent • Phone Control • Cloud / Server / Laptop${RESET}           ${BRIGHT_PURPLE}│${RESET}
${BRIGHT_PURPLE}  │${RESET}                                                                          ${BRIGHT_PURPLE}│${RESET}
${BRIGHT_PURPLE}  │${RESET}   ${GRAY}Brain Model${RESET}     ${BOLD}nvidia/Llama-3.1-Nemotron-70B-Instruct${RESET}                 ${BRIGHT_PURPLE}│${RESET}
${BRIGHT_PURPLE}  │${RESET}   ${GRAY}Inference${RESET}       ${CYAN}Nebius Serverless / Token Factory${RESET}                     ${BRIGHT_PURPLE}│${RESET}
${BRIGHT_PURPLE}  │${RESET}   ${GRAY}Cognitive Core${RESET}  ${YELLOW}Hermes Agent (Nous Research Skills Engine)${RESET}             ${BRIGHT_PURPLE}│${RESET}
${BRIGHT_PURPLE}  │${RESET}   ${GRAY}Sandboxing${RESET}      ${PURPLE}NVIDIA OpenShell (Landlock + Seccomp BPF)${RESET}              ${BRIGHT_PURPLE}│${RESET}
${BRIGHT_PURPLE}  │${RESET}   ${GRAY}Web Engine${RESET}      ${BRIGHT_CYAN}Obscura Stealth Headless Browser (Playwright)${RESET}          ${BRIGHT_PURPLE}│${RESET}
${BRIGHT_PURPLE}  │${RESET}   ${GRAY}Storage Tier${RESET}    ${GREEN}Dual Vaults: shared_vault.db + personal_vault.db${RESET}       ${BRIGHT_PURPLE}│${RESET}
${BRIGHT_PURPLE}  │${RESET}   ${GRAY}Active Role${RESET}     ${BOLD}${nodeRole}${RESET}                                     ${BRIGHT_PURPLE}│${RESET}
${BRIGHT_PURPLE}  │${RESET}                                                                          ${BRIGHT_PURPLE}│${RESET}
${BRIGHT_PURPLE}  │${RESET}   ${BRIGHT_GREEN}● SYSTEM OPERATIONAL${RESET}  ${DIM}│ ${extraDetail || 'Telegram & Offloading Ready'}${RESET}          ${BRIGHT_PURPLE}│${RESET}
${BRIGHT_PURPLE}  ╰──────────────────────────────────────────────────────────────────────────╯${RESET}
`;
    console.log(banner);
}

module.exports = { printBanner };
