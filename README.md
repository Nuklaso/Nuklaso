<div align="center">

<img src="https://raw.githubusercontent.com/Nuklaso/Nuklaso/main/hero.svg" width="100%"/>

<img src="https://readme-typing-svg.demolab.com?font=VT323&size=32&duration=2600&pause=700&color=00FF41&background=00000000&center=true&vCenter=true&width=900&height=50&lines=root%40nuklaso%3A~%23+wake+up...;root%40nuklaso%3A~%23+the+stack+has+you.;root%40nuklaso%3A~%23+i+build+at+both+ends+of+it.;root%40nuklaso%3A~%23+._"/>

<img src="https://raw.githubusercontent.com/Nuklaso/Nuklaso/main/orbit.svg" width="100%"/>

</div>

## `▌ 01 — BOOT`

```console
[    0.000000] nuklaso boot loader v3.0 — handing control to profile kernel
[    0.000412] probing operator .................................. [  OK  ]
[    0.001183] mounting /dev/web      frontend · backend · full-stack    [  OK  ]
[    0.002047] mounting /dev/systems  kernel · memory · scheduler        [  OK  ]
[    0.003911] loading  typescript.ko  rust.ko  c.ko  x86_64_asm.ko ... [  OK  ]
[    0.006774] enabling long mode · paging · APIC ................ [  OK  ]
[    0.008230] spawning scheduler  pid 1 ......................... [  OK  ]
[    0.011905] flagship process  [OS_PROJECT_NAME] ............... [ ACTIVE ]
[    0.017001] reality.sys ....................................... [ FAILED ]
[    0.017002]   └─ falling back to terminal.sys ................. [  OK  ]

nuklaso login: root
Password: ************

  Welcome to the real stack.
```

## `▌ 02 — WHOAMI`

```console
root@nuklaso:~# neofetch

    1 0 ｱ 1 ﾂ 0 ﾈ        root@nuklaso
    ﾑ 1 0 ﾂ ｻ 1 0        ────────────────────────────────────────────────
    0 ｷ 1 ﾈ 0 1 ﾀ        OS ........... [OS_PROJECT_NAME] v0.4.0  (self-built)
    1 ﾐ 0 ｹ 1 ﾂ 0        Kernel ....... monolithic · x86_64 · preemptive
    ｼ 0 1 ﾏ 0 ﾑ 1        Bootloader ... custom UEFI stage-1 → ELF64 stage-2
    0 1 ﾈ 0 ｶ 1 ﾂ        Shell ........ zsh · nvim · tmux · zero mouse input
    ﾇ 0 1 ｻ 1 0 ﾏ        Uptime ....... [X] years shipping to production
    1 ﾀ 0 1 ﾈ 0 ｹ        Role ......... Full-Stack Web Engineer
    0 ﾂ 1 0 ﾐ 1 ﾑ        Building ..... an OS, from CPU instruction zero
    ｷ 1 0 ﾈ 0 ｼ 1        Languages .... TypeScript · Rust · C · x86_64 ASM
    1 0 1 ﾂ 1 0 ﾀ        Memory ....... 4-level paging + slab allocator
    0 ﾑ 1 ｹ 0 ﾏ 0        Debugger ..... QEMU + GDB remote, break at _start
                         Location ..... [LOCATION]
    ███ ███ ███ ███      Status ....... ● ACTIVE — open to serious builds
    ▀▀▀ ▀▀▀ ▀▀▀ ▀▀▀

root@nuklaso:~# cat /proc/self/mission
"Own the whole stack. From the page table to the pixel."
```

> **Most engineers pick one layer of the stack and live there for a career.**
> I refuse to. By day I ship production web systems that real users hit.
> By night I write the kernel those systems could one day run on.

<table>
<tr>
<td width="50%" valign="top">

**`/dev/web` — the top**

```diff
+ professional, actively shipping full-stack dev
+ production traffic, real SLAs, real on-call
+ design systems · a11y · sub-second LCP
+ typed end-to-end: schema → API → client → UI
! if the build takes 3 minutes, that is a bug
```

</td>
<td width="50%" valign="top">

**`/dev/systems` — the bottom**

```diff
+ [OS_PROJECT_NAME] — full OS, written from zero
+ bootloader → long mode → GDT/IDT/TSS → APIC
+ paging · PMM · VMM · slab heap · scheduler
+ drivers: PS/2 · HPET · serial · fb · AHCI
! no fork. no base distro. no shortcuts.
```

</td>
</tr>
</table>

## `▌ 03 — OPERATING RANGE`

<div align="center">
<img src="https://raw.githubusercontent.com/Nuklaso/Nuklaso/main/stack3d.svg" width="100%"/>
</div>

## `▌ 04 — FLAGSHIP`

```console
root@nuklaso:~# systemctl status [OS_PROJECT_NAME]

● [OS_PROJECT_NAME].service — an operating system built from absolute zero
     Loaded: loaded (/src/kernel; enabled)
     Active: ● active (building)  since [START_DATE]
   Language: C · x86_64 Assembly · Rust
     Target: x86_64-unknown-none · UEFI · QEMU + real hardware

   SUBSYSTEM        IMPLEMENTATION                          PROGRESS
   ───────────────  ─────────────────────────────────────   ──────────────────
   bootloader       UEFI stub + stage-2, ELF64 parsing      ██████████████ done
   memory           4-level paging, PMM, VMM, slab heap     ██████████████ done
   interrupts       GDT / IDT / TSS, APIC + IOAPIC          ██████████████ done
   scheduler        preemptive RR, threads, ctx switch      █████████████░ done
   drivers          PS/2, HPET, serial, fb, AHCI            █████████░░░░░ wip
   filesystem       VFS layer + FAT32 / custom FS           ███████░░░░░░░ wip
   userspace        ring-3, syscall ABI, ELF loader         ████░░░░░░░░░░ wip
   shell            native userspace shell + coreutils      █░░░░░░░░░░░░░ next
   network          e1000 driver, ARP / IPv4 / TCP          ░░░░░░░░░░░░░░ next
   ───────────────────────────────────────────────────────────────────────────
   no fork. no base distro. every instruction written by hand.
```

<div align="center">
<a href="[PROJECT_LINK]"><img src="https://img.shields.io/badge/SOURCE-000000?style=for-the-badge&logo=github&logoColor=00ff41&labelColor=000000&color=003b12"/></a>
<a href="[DEMO_LINK]"><img src="https://img.shields.io/badge/BOOT_DEMO-000000?style=for-the-badge&logo=qemu&logoColor=00ff41&labelColor=000000&color=003b12"/></a>
<a href="[DOCS_LINK]"><img src="https://img.shields.io/badge/DEV_LOG-000000?style=for-the-badge&logo=readthedocs&logoColor=00ff41&labelColor=000000&color=003b12"/></a>
</div>

## `▌ 05 — PAYLOADS`

```console
root@nuklaso:~# ./loadout --arm --all

  decrypting arsenal  [████████████████████████████████████]  6/6  ARMED

  ID     PAYLOAD            CLASS        VECTOR                    IMPACT
  ─────  ─────────────────  ───────────  ────────────────────────  ────────
  P-01   kernel-forge       SYSTEMS      bare-metal / x86_64       CRITICAL
  P-02   ghost-deploy       DEPLOYMENT   blue-green · autorollback HIGH
  P-03   recon-crawler      RECON        headless · distributed    MEDIUM
  P-04   hydra-scaffold     AUTOMATION   schema → full-stack       HIGH
  P-05   blackbox-audit     SECURITY     cve · secrets · headers   CRITICAL
  P-06   dead-drop          INFRA        encrypted secret sync     CRITICAL
```

<table>
<tr><th align="left" width="19%">PAYLOAD</th><th align="left" width="49%">PURPOSE</th><th align="left" width="20%">VECTOR</th><th align="center" width="12%"></th></tr>

<tr><td valign="top"><code>kernel-forge</code><br/><sub>🔴 CRITICAL</sub></td>
<td valign="top">One-command bare-metal pipeline. Bootstraps the cross-compiler, assembles linker scripts, builds a bootable ISO, launches QEMU and attaches GDB. A 40-minute OS-dev ritual reduced to <code>make run</code>.</td>
<td valign="top"><code>C</code> <code>ASM</code> <code>QEMU</code></td>
<td align="center" valign="top"><a href="[PROJECT_LINK]"><img src="https://img.shields.io/badge/▶-000000?style=flat-square&labelColor=000000&color=00ff41"/></a></td></tr>

<tr><td valign="top"><code>ghost-deploy</code><br/><sub>🟠 HIGH</sub></td>
<td valign="top">Zero-downtime deployment chain — atomic blue/green swap, health-probe gating, auto-rollback on 5xx spike. Ships to prod without dropping a single connection.</td>
<td valign="top"><code>Docker</code> <code>Actions</code></td>
<td align="center" valign="top"><a href="[PROJECT_LINK]"><img src="https://img.shields.io/badge/▶-000000?style=flat-square&labelColor=000000&color=00ff41"/></a></td></tr>

<tr><td valign="top"><code>recon-crawler</code><br/><sub>🟡 MEDIUM</sub></td>
<td valign="top">Distributed headless recon engine. Fingerprints target stacks, maps public surface area, diffs it over time, exports structured intel. Rate-limit aware, politely relentless.</td>
<td valign="top"><code>TS</code> <code>Playwright</code></td>
<td align="center" valign="top"><a href="[PROJECT_LINK]"><img src="https://img.shields.io/badge/▶-000000?style=flat-square&labelColor=000000&color=00ff41"/></a></td></tr>

<tr><td valign="top"><code>hydra-scaffold</code><br/><sub>🟠 HIGH</sub></td>
<td valign="top">Schema in — typed API, client SDK, migrations, auth and admin panel out. Cut off one endpoint and two more generate in its place.</td>
<td valign="top"><code>Node</code> <code>Prisma</code> <code>tRPC</code></td>
<td align="center" valign="top"><a href="[PROJECT_LINK]"><img src="https://img.shields.io/badge/▶-000000?style=flat-square&labelColor=000000&color=00ff41"/></a></td></tr>

<tr><td valign="top"><code>blackbox-audit</code><br/><sub>🔴 CRITICAL</sub></td>
<td valign="top">Pre-merge security sweep — dependency CVEs, leaked secrets, CSP/HSTS verification, supply-chain integrity. Fails the build before an attacker finds it first.</td>
<td valign="top"><code>Python</code> <code>Trivy</code></td>
<td align="center" valign="top"><a href="[PROJECT_LINK]"><img src="https://img.shields.io/badge/▶-000000?style=flat-square&labelColor=000000&color=00ff41"/></a></td></tr>

<tr><td valign="top"><code>dead-drop</code><br/><sub>🔴 CRITICAL</sub></td>
<td valign="top">Encrypted secret distribution — age-encrypted at rest, short-lived tokens in flight, full audit trail. Secrets that exist only exactly when and where they are needed.</td>
<td valign="top"><code>Rust</code> <code>Terraform</code></td>
<td align="center" valign="top"><a href="[PROJECT_LINK]"><img src="https://img.shields.io/badge/▶-000000?style=flat-square&labelColor=000000&color=00ff41"/></a></td></tr>

</table>

## `▌ 06 — SHIPPED`

<div align="center">

<a href="[PROJECT_LINK]"><img src="https://github-readme-stats.vercel.app/api/pin/?username=Nuklaso&repo=[REPO_NAME_1]&bg_color=000000&title_color=00ff41&icon_color=00ff41&text_color=00b32d&border_color=00ff41&border_radius=4" width="49%"/></a>
<a href="[PROJECT_LINK]"><img src="https://github-readme-stats.vercel.app/api/pin/?username=Nuklaso&repo=[REPO_NAME_2]&bg_color=000000&title_color=00ff41&icon_color=00ff41&text_color=00b32d&border_color=00ff41&border_radius=4" width="49%"/></a>
<a href="[PROJECT_LINK]"><img src="https://github-readme-stats.vercel.app/api/pin/?username=Nuklaso&repo=[REPO_NAME_3]&bg_color=000000&title_color=00ff41&icon_color=00ff41&text_color=00b32d&border_color=00ff41&border_radius=4" width="49%"/></a>
<a href="[PROJECT_LINK]"><img src="https://github-readme-stats.vercel.app/api/pin/?username=Nuklaso&repo=[REPO_NAME_4]&bg_color=000000&title_color=00ff41&icon_color=00ff41&text_color=00b32d&border_color=00ff41&border_radius=4" width="49%"/></a>

</div>

<details>
<summary><b>&nbsp;▸&nbsp; <code>cat ~/shipped/archive.log</code></b></summary>
<br/>

| PROJECT | PITCH | STACK | LINKS |
|:--|:--|:--|:--|
| **[PROJECT_NAME_5]** | One-line pitch: the problem, the punch. | `Astro` `TS` `Cloudflare` | [code]([PROJECT_LINK]) · [live]([DEMO_LINK]) |
| **[PROJECT_NAME_6]** | One-line pitch: the problem, the punch. | `FastAPI` `ClickHouse` | [code]([PROJECT_LINK]) · [live]([DEMO_LINK]) |
| **[PROJECT_NAME_7]** | One-line pitch: the problem, the punch. | `C` `SDL2` `OpenGL` | [code]([PROJECT_LINK]) · [live]([DEMO_LINK]) |
| **[PROJECT_NAME_8]** | One-line pitch: the problem, the punch. | `Rust` `WASM` `Vite` | [code]([PROJECT_LINK]) · [live]([DEMO_LINK]) |

</details>

## `▌ 07 — TELEMETRY`

<div align="center">

<img src="https://github-readme-stats.vercel.app/api?username=Nuklaso&show_icons=true&count_private=true&include_all_commits=true&bg_color=000000&title_color=00ff41&icon_color=00ff41&text_color=00b32d&border_color=00ff41&border_radius=4&ring_color=00ff41" height="180"/>
<img src="https://streak-stats.demolab.com?user=Nuklaso&background=000000&border=00ff41&stroke=00ff41&ring=00ff41&fire=00ff41&currStreakNum=00ff41&currStreakLabel=00ff41&sideNums=00b32d&sideLabels=00b32d&dates=006b1c&border_radius=4" height="180"/>

<img src="https://github-readme-stats.vercel.app/api/top-langs/?username=Nuklaso&layout=compact&langs_count=10&bg_color=000000&title_color=00ff41&text_color=00b32d&border_color=00ff41&border_radius=4" height="172"/>
<img src="https://github-profile-trophy.vercel.app/?username=Nuklaso&theme=matrix&no-frame=true&no-bg=true&column=3&row=3&margin-w=8&margin-h=8" height="172"/>

<img src="https://github-readme-activity-graph.vercel.app/graph?username=Nuklaso&custom_title=SIGNAL%20TRACE%20%2F%2F%20LAST%2031%20DAYS&bg_color=000000&color=00ff41&line=00ff41&point=d7ffd7&area=true&area_color=00ff41&title_color=00ff41&hide_border=false&border_color=00ff41&radius=4" width="100%"/>

`root@nuklaso:~# ./snake --devour ~/.contributions`

<img src="https://raw.githubusercontent.com/Nuklaso/Nuklaso/output/snake-matrix.svg" width="100%"/>

</div>

<details>
<summary><b>&nbsp;▸&nbsp; snake setup — needs one workflow file</b></summary>
<br/>

Create `.github/workflows/snake.yml`, commit, then **Actions → generate snake → Run workflow** once.

```yaml
name: generate snake

on:
  schedule: [{ cron: "0 */12 * * *" }]
  workflow_dispatch:
  push: { branches: [main] }

jobs:
  build:
    runs-on: ubuntu-latest
    permissions: { contents: write }
    steps:
      - uses: Platane/snk@v3
        with:
          github_user_name: Nuklaso
          outputs: |
            dist/snake-matrix.svg?palette=github-dark&color_snake=%2300ff41&color_dots=%23000000,%23003b12,%23007a26,%2300b32d,%2300ff41
      - uses: crazy-max/ghaction-github-pages@v4
        with: { target_branch: output, build_dir: dist }
        env: { GITHUB_TOKEN: "${{ secrets.GITHUB_TOKEN }}" }
```

</details>

## `▌ 08 — CONNECT`

<div align="center">

```console
root@nuklaso:~# nc -lvnp 1337 --accept inbound-collabs
[+] listening on 0.0.0.0:1337 — awaiting handshake
```

<a href="https://github.com/Nuklaso"><img src="https://img.shields.io/badge/GITHUB-000000?style=for-the-badge&logo=github&logoColor=00ff41&labelColor=000000&color=003b12"/></a>
<a href="[PORTFOLIO_URL]"><img src="https://img.shields.io/badge/PORTFOLIO-000000?style=for-the-badge&logo=firefoxbrowser&logoColor=00ff41&labelColor=000000&color=003b12"/></a>
<a href="[LINKEDIN_URL]"><img src="https://img.shields.io/badge/LINKEDIN-000000?style=for-the-badge&logo=linkedin&logoColor=00ff41&labelColor=000000&color=003b12"/></a>
<a href="[TWITTER_URL]"><img src="https://img.shields.io/badge/X-000000?style=for-the-badge&logo=x&logoColor=00ff41&labelColor=000000&color=003b12"/></a>
<a href="[DISCORD_URL]"><img src="https://img.shields.io/badge/DISCORD-000000?style=for-the-badge&logo=discord&logoColor=00ff41&labelColor=000000&color=003b12"/></a>
<a href="mailto:[EMAIL]"><img src="https://img.shields.io/badge/EMAIL-000000?style=for-the-badge&logo=maildotru&logoColor=00ff41&labelColor=000000&color=003b12"/></a>

</div>

## `▌ 09 — HALT`

```console
root@nuklaso:~# cat ~/.signature

    Most people build ON the platform.
    I build the platform.

    From the bootloader that hands control to the kernel,
    to the render pass that paints the final pixel —
    it is all just instructions.

    I intend to write every single one of them.

                                                   — [YOUR_NAME]

root@nuklaso:~# shutdown -h now

[ 9999.999999] unmounting /dev/web ............................... [  OK  ]
[ 9999.999999] flushing scheduler queue .......................... [  OK  ]
[ 9999.999999] there is no spoon ................................. [  OK  ]

  System halted.  Wake up.
```

<div align="center">

<img src="https://komarev.com/ghpvc/?username=Nuklaso&style=for-the-badge&color=00ff41&labelColor=000000&label=SESSIONS+TRACED"/>
<img src="https://img.shields.io/github/followers/Nuklaso?style=for-the-badge&logo=github&logoColor=00ff41&labelColor=000000&color=003b12&label=OPERATORS"/>

<img src="https://raw.githubusercontent.com/Nuklaso/Nuklaso/main/matrix.svg" width="100%"/>

</div>
