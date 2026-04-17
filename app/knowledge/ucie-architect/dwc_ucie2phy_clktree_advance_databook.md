**DesignWareCore ****UCIE**** PHY**

Data book

UCIE2PHY Clock Tree for Advanced package

dwc_ucie2phy_clktree

Version 1.3

Jan 30, 2026

Copyright Notice and Proprietary Information Notice

Copyright © 2025 Synopsys, Inc. All rights reserved. This software and documentation contain confidential and proprietary information that is the property of Synopsys, Inc. The software and documentation are furnished under a license agreement and may be used or copied only in accordance with the terms of the license agreement. No part of the software and documentation may be reproduced, transmitted, or translated, in any form or by any means, electronic, mechanical, manual, optical, or otherwise, without prior written permission of Synopsys, Inc., or as expressly provided by the license agreement.

Destination Control Statement

All technical data contained in this publication is subject to the export control laws of the United States of America. Disclosure to nationals of other countries contrary to United States law is prohibited. It is the reader's responsibility to determine the applicable regulations and to comply with them.

Disclaimer

SYNOPSYS, INC., AND ITS LICENSORS MAKE NO WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, WITH REGARD TO THIS MATERIAL, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.

Trademarks

Synopsys and certain Synopsys product names are trademarks of Synopsys, as set forth at

All other product or company names may be trademarks of their respective owners.

Synopsys, Inc.690 E. Middlefield RoadMountain View, CA 94043

Contents

Revision History

| Date | Owner | Revision | Description |
| --- | --- | --- | --- |
| **Apr 2****9****, 2024** | Hai Tran/ Dao Tran | 0.1 | Initial version |
| **May 21, 2024** | Hai Tran/ Dao Tran | 0.2 | Update Figure 32 Write clock tree at DW x64: add PHYClk, update cal_clk path Update Figure 35 DW x64 Read clock** tree**: remove S2D, move occ_mux into RXCK Update **Error! Reference source not found.**: add PHYclk connection |
| **May 29, 2024** | Dao Tran | 0.3 | Follow the jira Add 2 new cells dwc_ucie2phy_clkbuf_iocal, dwc_ucie2phy_clkbuf_iocal_load for IOCAL purpose Update the **Error! Reference source not found.** & **Error! Reference source not found.** |
| **Jun 03, 2024** | Dao Tran | 0.4 | Follow the Jira P80001562-529033 Add the Std cell loading for PhyClk’s occ_mux replica Update the **Error! Reference source not found.** |
| **Jun 11, 2024** | Hai Tran | 0.41 | Update Figure 32 Write clock tree at DW x64 : Add dwc_ucie2phy_txcal for data & clk path Add dwc_ucie2phy_clkbuf_iocal & dwc_ucie2phy_clkbuf_iocal_load at last stage to IOCAL purpose Update Figure 35 DW x64 Read clock** tree** Add dwc_ucie2phy_clkbuf_iocal & dwc_ucie2phy_clkbuf_iocal_load at last stage to IOCAL purpose Add dwc_ucie2phy_rxcal into READ Clock treescheme |
| **Jul 18, 2024** | Hai Tran | 0.42 | Update Figure 32 Write clock tree at DW x64: Add missing clkbuf_iocal & clkbuf_iocal_load in clk path Add POR Update Figure 35 DW x64 Read clock** tree** Define VDDREG domain for each clock cell |
| **Jul 25, 2024** | Hai Tran | 0.43 | Correct cell name in Figure 25 Clock buffer cell list Correct Table 217 Clock buffer pin 3-in-3-out in READ Clock tree description: update pin names to clk_in, clk_in_b, clk_out & clk_out_b |
| **Aug**** ****1****, 2024** | Hai Tran | 0.5 | Add section 2.4 **Error! Reference source not found.** Update Figure 32 Write clock tree at DW x64: Add TRK function Update Figure 35 DW x64 Read clock** tree**: add vreg common, change clkbuf_ra3 to 4-in-4-out Update Figure 212 Clock buffer 3-in-3-out in READ Clock tree block diagram, Figure 214 Clock buffer 5-in-5-out in READ Clock tree block diagram & Figure 220 Mux 4 to 2 in READ Clock tree block diagram: change input power pin from VDDREG to VDD |
| **Aug**** 2****1****, 202****4** | Dao Tran | 0.6 | Update Figure 32 Write clock tree at DW x64: Remove TX_CAL for CK* group, remove all iocal_* cells, Update in CK_TRK path, Remove custom path for PhyClk (only support std-cell buffer loading) Update Figure 35 DW x64 Read clock** tree**: Remove RX_CAL for, remove all iocal_* cells, Add std-cell loading(AN2, MUX2), Swap location of RXTRK and RXCKRD. Update name of VREG cells. Update PCLK in PHY-Top connection (section 3.6), update Pre-mapped cells list (section 3.7) All the updates are follow the jira and alignments in clocking structure: **Add ****input ****pin rfb_en** to enable Resitive Feedback feature in high-freq range operation for clkbuf_wa1, clkbuf_ra1, muxwa1 |
| **Aug 23, 202****4** | Dao Tran | 0.61 | Add pin VDDREG for clkbuf_ra1. Update description for the “rfb_en” pin: add “Set to 0 if the input clock is static/off (idle state/LP mode)” |
| **Sep 05, 2024** | Dao Tran | 0.62 | Update section 3.1- X64 – Write clock tree: Add VRED_VDD supply connection for LCDLs. Remove CTL_CLK buffer: No more support in UCIe2 Remove _iocal_* cell : No more support in production. |
| **Sep ****2****7****, 2024** | Dao Tran | 0.7 | *** Update for Dec-TC (Follow request from DI: Support custom the RxClkOut path) Update section 3.1- X64 – Write clock tree: Add custom path for RxClkOut connection. *** Update for Production: Update DCD location in RX region for I/Q detection support Section 3.2- X64 – Read clock tree Update PHY Pclk connection Add new cell: dwc_ucie2phy_clkbuf_phywa4 section 3.3 Pclk in PHY TOP |
| **Oct 07, 2024** | Dao Tran | 0.71 | Add section 3.2 and section 3.4 for Dec-TC specification. |
| **Oct ****17****, 2024** | Dao Tran | 0.72 | Follow the jira To solve the unstable output clock of PhaseGen. Add new loading cells for delay skew blalancing between TxClk_DATA and TxClk_CK: dwc_ucie2phy_clkload1_tx, dwc_ucie2phy_clkload2_tx Update section 3.2 X64 – Write clock tree : Change location of TX_CAL, Add new Loading cells connection. |
| **Oct ****28****, 2024** | Dao Tran | 0.73 | Update section 3.2 X64 – Write clock tree: Add custom connection for TXCKP/TXCKN RXCKP/RXCKN Loopback support. |
| **Nov**** ****0****8****, 2024** | Dao Tran | 0.74 | Update section 3.2 X64 – Write clock tree: update connections of input Muxwa1. Add AND pre-map loadings for the RxClkOut paths, that follow latest Arch-Spec Update section 3.4 X64 – Read clock tree: remove pre-map loadings, that follow latest Arch-Spec To avoid confusion, detail updates will be clarified on the Jira |
| **Dec**** ****10****, 2024** | Dao Tran | 0.75 | Update Section: 3.5 x64 - Read clock tree inside DWORD Replace one rx_load cell connection by RX_CAL cell connection at RXs group VREG7 |
| **Jan**** ****1****4****, 202****5** | Dao Tran | 0.76 | **Just for document cleaning purpose. No****thing**** function****al****/connection update.** Fix typo and add txdcd location, update the IO FP. Section: 3.2 x64 - Write clock tree inside DWORD Section: 3.5 x64 - Read clock tree inside DWORD |
| **Apr 11, 2025** | Tri Vo | 0.8 | Change cell name to follow new conventional name (UCIe-A/S and PHY orientation) |
| **Apr 13, 2025** | Dao Tran | 0.81 | Update The sections Clock Tree Architecture for consistency new cell name update |
| **May 9, 2025** | Quynh Tong | 0.82 | Update cell list – Add new cells: dwc_ucie2phy_clkbufw4_a, dwc_ucie2phy_clkbufw5_a Change cell name following new conventional name (remove PHY orientation _ns/ew) |
| **May**** 15****, 2025** | Quynh Tong | 0.83 | Change cell name following new conventional name: remove _a for cells dwc_ucie2phy_dca/dcd/lcdl/por/tx_cal/vreg* |
| **Jun 10, 2025** | Tri Vo | 0.85 | Change read clock buffer/load supply from VDD to VDDREG |
| **Jul 04, 2025** | Tri Vo | 0.86 | dwc_ucie2phy_clkloadrx: change VDDREG back to VDD domain |
| **Jul 12, 2025** | Tri Vo | 0.9 | Update clkbufr1/2/3: add new pin clksim_in/out to support SIM Update clkrxload: Add new pin X_SIM to support SIM Change VDDREG to VDD Add new DW read clock tree with SIM |
| **Sep 08, 2025** | Tri Vo | 0.91 | Update DW Write/Read clock tree: swap location of data11 vs data12 and data51 vs data52 () |
| **Ọ****ct 29, 2025** | Tri Vo | 1.0 | Add clock tree for UCIe-A x32 configuration. New buffer for x32 config: dwc_ucie2phy_clkbufw6_a dwc_ucie2phy_clkbufw7_a dwc_ucie2phy_clkbufw8_a dwc_ucie2phy_clkbufw9_a dwc_ucie2phy_clkbufw10_a dwc_ucie2phy_clkgt2_a dwc_ucie2phy_clkbufr4_a Clock for DFT: replace buffer by OCC mux to optimize timing () Loopback connection: support connection from TXTRK and TXCKRD to RXTRK and RXCKRD |
| **Nov 17, 2025** | Tri Vo | 1.1 | clkbufphyw1_a: add pin clk_en () Add section 3.6 describing the MMPL clock tree with enable signal |
| **Dec 29, 2025** | Tri Vo | 1.2 | Remove Clock mux for Track TX () New buffer dwc_ucie2phy_clkbufw11_a (replace muxw1_a) Update Write clock tree x16 and x32 |
| **Jan 11, 2026** | Tri Vo | 1.21 | New buffer dwc_ucie2phy_lclkbuf_a |
| **Jan 30, 2026** | Tri Vo | 1.3 | New buffer dwc_ucie2phy_lclkbuf1_a () Add spec for lclkbuf* |

Reference Documents

# Introduction

## Overview

This Databook describes the information of clock buffer library for UCIe2 PHY, including design feature, electrical specification and clock tree integration guideline.

This library provides the set of clock buffers and clock gating that optimized for high speed clock distribution, low latency, skew and jitter requirement.

## Design features

Supports x64 config, 64TX, 64RX

Supports x32 config, 32TX, 32RX

Maximum clock frequency: 10GHz

## Cell list

Table 11 - Cell list

| **#** | **Cell name** | **Description** |
| --- | --- | --- |
| 1 | dwc_ucie2phy_clkbufr1_a | Read Clock tree buffer 2-in-2-out: drive longest vertical route |
| 2 | dwc_ucie2phy_clkbufr2_a | Read Clock tree buffer 2-in-2-out: placed at each group |
| 3 | dwc_ucie2phy_clkbufr3_a | Read Clock tree buffer 4-in-4-out: last stage buffer |
| 4 | dwc_ucie2phy_clkbufr4_a | Read Clock tree buffer 2-in-2-out: drive longest vertical route (for x32 configuration) |
| 5 | dwc_ucie2phy_clkbufw1_a | DW Write Clock tree buffer – input DW |
| 6 | dwc_ucie2phy_clkbufw2_a | DW Write Clock tree buffer 2-in-2-out – placed after Phase gen |
| 7 | dwc_ucie2phy_clkbufw3_a | DW Write Clock tree buffer 2-in-2-out – placed at each IO row |
| 8 | dwc_ucie2phy_clkbufw4_a | DW Write Clock tree buffer – support TRK function |
| 9 | dwc_ucie2phy_clkbufw5_a | DW Write Clock tree buffer – support Loopback function |
| 10 | dwc_ucie2phy_clkbufw6_a | DW Write Clock tree buffer – input DW (for x32 configuration) |
| 11 | dwc_ucie2phy_clkbufw7_a | DW Write Clock tree buffer 2-in-2-out – placed after Phase gen (for x32 configuration) |
| 12 | dwc_ucie2phy_clkbufw8_a | DW Write Clock tree buffer 2-in-2-out – placed at each group (for x32 configuration) |
| 13 | dwc_ucie2phy_clkbufw9_a | DW Write Clock tree buffer – support TRK function (for x32 configuration) |
| 14 | dwc_ucie2phy_clkbufw10_a | DW Write Clock tree buffer – support Loopback function (for x32 configuration) |
| 15 | dwc_ucie2phy_clkbufw11_a | DW Write Clock tree buffer 2-in-2-out – placed at each IO group (applicable for both x32 and x64 configuration) |
| 16 | dwc_ucie2phy_clkgt_a | DW Write Clock tree clock gate for pclk |
| 17 | dwc_ucie2phy_clkgt1_a | DW Write Clock tree clock gate for cal_clk |
| 18 | dwc_ucie2phy_clkgt2_a | DW Write Clock tree clock gate for pclk (for x32 configuration) |
| 19 | dwc_ucie2phy_muxr1_a | Read Clock tree mux 4-in-2-out: placed after RXCK |
| 20 | dwc_ucie2phy_muxw2_a | DW Write Clock tree mux for cal_clk |
| 21 | dwc_ucie2phy_clkbufphyw1_a | PHYTOP Clock tree buffer – placed in MMPL |
| 22 | dwc_ucie2phy_clkbufphyw2_a | PHYTOP Clock tree buffer – placed in DW |
| 23 | dwc_ucie2phy_clkbufphyw3_a | PHYTOP Clock tree buffer – placed in MMPL for PLL isolate load |
| 24 | dwc_ucie2phy_clkbufphyw4_a | PHYTOP Clock tree buffer – placed in DW |
| 25 | dwc_ucie2phy_clkloadrx_a | Dummy load IO RX |
| 26 | dwc_ucie2phy_clkloadtx_a | Dummy load IO TX |
| 27 | dwc_ucie2phy_clkload1tx_a | Dummy load Txclk_CK |
| 28 | dwc_ucie2phy_clkload2tx_a | Dummy load TXclk_CK |
| 29 | dwc_ucie2phy_lclkbuf_a | LCLK buffer. DI uses this buffer to build LCLK tree |
| 30 | dwc_ucie2phy_lclkbuf1_a | LCLK buffer. DI uses this buffer to build LCLK tree |

# Functional Description

## Clock buffer

Figure 21 Clock buffer cell list

| **#** | **Cell name** | **Description** |
| --- | --- | --- |
| 1 | dwc_ucie2phy_clkbufphyw1_a | PHYTOP Clock tree buffer – placed in MMPL |
| 2 | dwc_ucie2phy_clkbufphyw2_a | PHYTOP Clock tree buffer – placed in DW |
| 3 | dwc_ucie2phy_clkbufphyw3_a | PHYTOP Clock tree buffer – placed in MMPL for PLL isolate load |
| 4 | dwc_ucie2phy_clkbufphyw4_a | PHYTOP Clock tree buffer – placed in DW |
| 5 | dwc_ucie2phy_lclkbuf_a | LCLK buffer. DI uses this buffer to build LCLK tree. Refer to Table 27 |
| 7 | dwc_ucie2phy_lclkbuf1_a | LCLK buffer. DI uses this buffer to build LCLK tree. Refer to Table 27 |

### Block diagram

Figure 22 Block diagram of clkbufphyw1_a

Figure 23 Block diagram of clkbufphyw2/3/4_a and lclkbuf_a/lclkbuf1_a

### Pin description

Table 21 Pin description of clkbufphyw1_a

| **No** | **Signal names** | **Direction** | **Type** | **Domain** | **Max frequency** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | clk_in | Input | Clock | VDD | 2 to 10 GHz | Input of buffer |
| 2 | clk_en | Input | Digital | VDD | - | Asynchronous enable. |
| 3 | clk_out | Output | Clock | VDD | 2 to 10 GHz | Output of buffer |
| 4 | VDD | Input | Power | VDD | - | Core power supply |
| 5 | VSS | input | Ground | VDD | - | Core ground |

Table 22 Pin description of clkbufphyw2/3/4_a

| **No** | **Signal names** | **Direction** | **Type** | **Domain** | **Max frequency** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | clk_in | Input | Clock | VDD | 2 to 10 GHz | Input of buffer |
| 2 | clk_out | Output | Clock | VDD | 2 to 10 GHz | Output of buffer |
| 3 | VDD | Input | Power | VDD | - | Core power supply |
| 4 | VSS | input | Ground | VDD | - | Core ground |

Table 23 Pin description of lclkbuf_a and lclkbuf1_a

| **No** | **Signal names** | **Direction** | **Type** | **Domain** | **Max frequency** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | clk_in | Input | Clock | VDD | 2.5 GHz | Input of buffer |
| 2 | clk_out | Output | Clock | VDD | 2.5 GHz | Output of buffer |
| 3 | VDD | Input | Power | VDD | - | Core power supply |
| 4 | VSS | input | Ground | VDD | - | Core ground |

### Truth table

Table 24 Truth table of clkbufphyw1_a

| **clk_en** | **c****lk_in** | **c****lk_out** |
| --- | --- | --- |
| 0 | X | 0 |
| 0 | Z | 0 |
| 1 | 0 | 0 |
| 1 | 1 | 1 |
| 1 | X | X |
| 1 | Z | Z |

Table 25 Truth table of clkbufphyw2/3/4_a and lclkbuf_a

| **c****lk_in** | **c****lk_out** |
| --- | --- |
| 0 | 0 |
| 1 | 1 |
| X | X |
| Z | Z |

Note: X = Unknown, Z = high Z

**Timing arcs**

Figure 24 Clock buffer timing diagram

Table 26 Clock buffer timing arc

| Pin name | Direction | Related pin | Sdf cond | Timing type | Timing sense |
| --- | --- | --- | --- | --- | --- |
| **clk_out**** (*)** | output | clk_en | NA | combinational | nonunate |
| **clk_out** | output | clk_in | NA | combinational | positive_unate |

(*) Only available in clkbufphyw1_a

### Spec for lclkbuf*

LCLKBUF* are custom buffers that PnR uses to build the clock tree for LCLK. The general specification:

Table 27 LCLKBUF specification

| Pin name | Direction | Cell name | Min | Typ | Max | Unit |
| --- | --- | --- | --- | --- | --- | --- |
| Fmax | Max input frequency | lclkbuf* |  |  | 2.5 | GHz |
| **Cmax** | Max loading | lclkbuf |  |  | 1 | pF |
|  |  | lclkbuf1 |  |  | 0.5 | pF |
| **Trf** | Transition time (10-90%VDD) | lclkbuf* |  |  | 50 | ps |
| **DCD** | Duty cycle distortion | lclkbuf* | -5 |  | +5 | % |

## Clock buffer with R feedback

### Overview

Figure 25 Clock buffer cell list

| **#** | **Cell name** | **Description** |
| --- | --- | --- |
| 1 | dwc_ucie2phy_clkbufw1_a | DW WRITE Clock tree buffer – input DW – x64 PHY config |
| 2 | dwc_ucie2phy_clkbufw4_a | DW WRITE Clock tree buffer – support TRK function – x64 PHY config |
| 3 | dwc_ucie2phy_clkbufw5_a | DW WRITE Clock tree buffer – support Loopback function – x64 PHY config |
| 4 | dwc_ucie2phy_clkbufw6_a | DW WRITE Clock tree buffer – input DW – x32 PHY config |
| 5 | dwc_ucie2phy_clkbufw9_a | DW WRITE Clock tree buffer – support TRK function – x32 PHY config |
| 6 | dwc_ucie2phy_clkbufw10_a | DW WRITE Clock tree buffer – support Loopback function – x32 PHY config |

### Block diagram

Figure 26 Clock buffer block diagram

### Pin description

Table 28 Clock buffer pin description

| **No** | **Signal names** | **Direction** | **Type** | **Domain** | **Max frequency** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | clk_in | Input | Clock | VDD | 2 to 10 GHz | Input of buffer, 10GHz for RX clkpath for TX clkpath |
| 2 | clk_out | Output | Clock | VDD | 2 to 10 GHz | Output of buffer, 10GHz for RX clkpath and for TX clkpath |
| 3 | rfb_en | Input | Digital | VDD | - | Resistive Feedback enable for high frequency operation 1: Enable resistive feedback. (Freq range 8Ghz - 10Ghz) 0: Disable resistive feedback. (Freq range 2Ghz - <8Ghz) Set to 0 if the input clock is static/off (idle state/LP mode). |
| 4 | VDD | Input | Power | VDD | - | Core power supply |
| 5 | VSS | input | Ground | VSS | - | Core ground |

### Truth table

Table 29 Clock buffer truth table

| **Clk_in** | **Clk_out** |
| --- | --- |
| 0 | 0 |
| 1 | 1 |
| X | X |
| Z | Z |

Note: X = Unknown, Z = high Z

### Timing arcs

Figure 27 Clock buffer timing diagram

Table 210 Clock buffer timing arc

| Pin name | Direction | Related pin | Sdf cond | Timing type | Timing sense |
| --- | --- | --- | --- | --- | --- |
| **clk_out** | output | clk_in | NA | combinational | positive_unate |

## Clock buffer 2-in-2-out in WRITE Clock tree

### Overview

| **#** | **Cell name** | **Description** |
| --- | --- | --- |
| 1 | dwc_ucie2phy_clkbufw2_a | DW Write Clock tree buffer 2-in-2-out – placed after Phase gen x64 PHY config |
| 2 | dwc_ucie2phy_clkbufw3_a | DW Write Clock tree buffer 2-in-2-out – placed at each IO row x64 PHY config |
| 3 | dwc_ucie2phy_clkbufw7_a | DW Write Clock tree buffer 2-in-2-out – placed after Phase gen x32 PHY config |
| 4 | dwc_ucie2phy_clkbufw8_a | DW Write Clock tree buffer 2-in-2-out – placed at each IO row x32 PHY config |
| 5 | dwc_ucie2phy_clkbufw11_a | DW Write Clock tree buffer 2-in-2-out – placed at each IO group. Applicable for both x64 and x32 PHY config |

### Block diagram

Figure 28 Clock buffer 2-in-2-out in WRITE Clock tree block diagram

### Pin description

Table 211 Clock buffer pin 2-in-2-out in WRITE Clock tree description

| **No** | **Signal name** | **Direction** | **Type** | **Domain** | **Max frequency** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | clk_in0 | Input | Clock | VDD | 2 to 10 GHz | Input of buffer |
| 2 | clk_in90 | Input | Clock | VDD | 2 to 10 GHz | Input of buffer |
| 3 | clk_out0 | Output | Clock | VDD | 2 to 10 GHz | Output of buffer |
| 4 | clk_out90 | Output | Clock | VDD | 2 to 10 GHz | Output of buffer |
| 5 | VDD | Input | Power | VDD | - | Core power supply |
| 6 | VSS | input | Ground | VSS | - | Core ground |

### Truth table

Table 212 Clock buffer 2-in-2-out in Write Clock tree truth table

| **c****lk_in0** | **c****lk_in90** | **c****lk_out0** | **c****lk_out90** |
| --- | --- | --- | --- |
| 0 | 0 | 0 | 0 |
| 1 | 1 | 1 | 1 |
| X | X | X | X |
| Z | Z | Z | Z |

Note: X = Unknown, Z = high Z

### Timing arcs

Figure 29 Clock buffer timing diagram

Table 213 Clock buffer 2-in-2-out in WRITE Clock tree timing arc

| Pin name | Direction | Related pin | Sdf cond | Timing type | Timing sense |
| --- | --- | --- | --- | --- | --- |
| **clk_out****0** | output | clk_in0 | NA | combinational | positive_unate |
| **clk_out90** | output | clk_in90 | NA | combinational | positive_unate |

## Clock buffer 3-in-3-out in READ Clock tree

### Overview

| **#** | **Cell name** | **Description** |
| --- | --- | --- |
| 1 | dwc_ucie2phy_clkbufr2_a | Read Clock tree buffer 3-in-3-out: placed at each group |

### Block diagram

Figure 210 Clock buffer 3-in-3-out in READ Clock tree block diagram

### Pin description

Table 214 Clock buffer pin 3-in-3-out in READ Clock tree description

| **No** | **Signal name** | **Direction** | **Type** | **Domain** | **Max frequency** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | clk_in | Input | Clock | VDDREG | 2 to 10 GHz | Input of buffer |
| 2 | clk_in_b | Input | Clock | VDDREG | 2 to 10 GHz | Input of buffer |
| 3 | clksim_in | Input | Clock | VDDREG | 2 to 10 GHz | SIM clock input |
| 4 | clk_out | Output | Clock | VDDREG | 2 to 10 GHz | Output of buffer |
| 5 | clk_out_b | Output | Clock | VDDREG | 2 to 10 GHz | Output of buffer |
| 6 | clksim_out | Output | Clock | VDDREG | 2 to 10 GHz | SIM clock output |
| 7 | VDDREG | Input | Power | VDDREG | - | Power supply |
| 8 | VSS | input | Ground | VSS | - | Core ground |

### Truth table

Table 215 Clock buffer 3-in-3-out in READ Clock tree truth table

| **Input** | **Output** | **Input** | **Output** | **Input** | **Output** |
| --- | --- | --- | --- | --- | --- |
| **clk_in** | **clk_out** | **clk_in_b** | **clk_out_b** | **clksim_in** | **clksim_out** |
| 0 | 0 | 0 | 0 | 0 | 0 |
| 1 | 1 | 1 | 1 | 1 | 1 |
| X | X | X | X | X | X |
| Z | Z | Z | Z | Z | Z |

Note: X = Unknown, Z = high Z

### Timing arcs

Figure 211 Clock buffer timing diagram

Table 216 Clock buffer timing arc

| Pin name | Direction | Related pin | Sdf cond | Timing type | Timing sense |
| --- | --- | --- | --- | --- | --- |
| **clk_out** | output | clk_in | NA | combinational | positive_unate |
| **clk_out_b** | output | clk_in_b | NA | combinational | positive_unate |
| **clksim_out** | output | clksim_in | NA | combinational | positive_unate |

## Clock buffer 3-in-3-out in READ Clock tree with R Feedback

### Overview

| **#** | **Cell name** | **Description** |
| --- | --- | --- |
| 1 | dwc_ucie2phy_clkbufr1_a | Read Clock tree buffer 3-in-3-out: drive longest vertical route – x64 PHY config |
| 2 | dwc_ucie2phy_clkbufr4_a | Read Clock tree buffer 3-in-3-out: drive longest vertical route – x32 PHY config |

### Block diagram

Figure 212 Clock buffer 3-in-3-out in READ Clock tree block diagram

### Pin description

Table 217 Clock buffer pin 3-in-3-out in READ Clock tree description

| **No** | **Signal name** | **Direction** | **Type** | **Domain** | **Max frequency** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | clk_in | Input | Clock | VDDREG | 2 to 10 GHz | Input of buffer |
| 2 | clk_in_b | Input | Clock | VDDREG | 2 to 10 GHz | Input of buffer |
| 3 | clksim_in | Input | Clock | VDDREG | 2 to 10 GHz | SIM clock input |
| 4 | clk_out | Output | Clock | VDDREG | 2 to 10 GHz | Output of buffer |
| 5 | clk_out_b | Output | Clock | VDDREG | 2 to 10 GHz | Output of buffer |
| 6 | clksim_out | Output | Clock | VDDREG | 2 to 10 GHz | SIM clock output |
| 7 | rfb_en | Input | Digital | VDD | - | Resistive Feedback enable for high frequency operation 1: Enable resistive feedback. (Freq range 8Ghz - 10Ghz) 0: Disable resistive feedback.(Freq range 2Ghz - <8Ghz) Set to 0 if the input clock is static/off (idle state/LP mode). |
| 8 | VDD | Input | Power | VDD | - | Power supply |
| 9 | VDDREG | Input | Power | VDDREG |  | Power supply |
| 10 | VSS | input | Ground | VDDREG | - | Core ground |

### Truth table

Table 218 Clock buffer 3-in-3-out in READ Clock tree truth table

| **Input** | **Output** | **Input** | **Output** | **Input** | **Output** |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **clk_in** | **rfb_en** | **clk_out** | **clk_in_b** | **rfb_en** | **clk_out_b** | **clksim_in** | **rfb_en** | **clksim_out** |
| 0 | 0/1 | 0 | 0 | 0/1 | 0 | 0 | 0/1 | 0 |
| 1 | 0/1 | 1 | 1 | 0/1 | 1 | 1 | 0/1 | 1 |
| X | 0/1 | X | X | 0/1 | X | X | 0/1 | X |
| Z | 0/1 | Z | Z | 0/1 | Z | Z | 0/1 | Z |

Note: X = Unknown, Z = high Z

### Timing arcs

Figure 213 Clock buffer timing diagram

Table 219 Clock buffer timing arc

| Pin name | Direction | Related pin | Sdf cond | Timing type | Timing sense |
| --- | --- | --- | --- | --- | --- |
| **clk_out** | output | clk_in | NA | combinational | positive_unate |
| **clk_out_b** | output | clk_in_b | NA | combinational | positive_unate |
| **clk****sim****_out** | output | clksim_in | NA | combinational | positive_unate |

## Clock buffer 5-in-5-out in READ Clock tree

### Overview

| **#** | **Cell name** | **Description** |
| --- | --- | --- |
| 1 | dwc_ucie2phy_clkbufr3_a | Read Clock tree buffer 5-in-5-out: drive longest vertical route |

### Block diagram

Figure 214 Clock buffer 5-in-5-out in READ Clock tree block diagram

### Pin description

Table 220 Clock buffer pin 5-in-5-out in READ Clock tree description

| **No** | **Signal name** | **Direction** | Type | **Domain** | **Max frequency** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| **1** | clk_in0 | Input | Clock | VDDREG | 2 to 10 GHz | Input of buffer |
| **2** | clk_in90 | Input | Clock | VDDREG | 2 to 10 GHz | Input of buffer |
| **3** | clk_in180 | Input | Clock | VDDREG | 2 to 10 GHz | Input of buffer |
| **4** | clk_in270 | Input | Clock | VDDREG | 2 to 10 GHz | Input of buffer |
| **5** | clksim_in | Input | Clock | VDDREG | 2 to 10 GHz | SIM input clock |
| **6** | clk_out0 | Output | Clock | VDDREG | 2 to 10 GHz | Output of buffer |
| **7** | clk_out90 | Output | Clock | VDDREG | 2 to 10 GHz | Output of buffer |
| **8** | clk_out180 | Output | Clock | VDDREG | 2 to 10 GHz | Output of buffer |
| **9** | clk_out270 | Output | Clock | VDDREG | 2 to 10 GHz | Output of buffer |
| **10** | clksim_out | Output | Clock | VDDREG | 2 to 10 GHz | SIM output clock |
| **11** | VDDREG | Input | Power | VDDREG | - | Power supply |
| **12** | VSS | Input | Ground | VSS | - | Core ground |

### Truth table

Table 221 Clock buffer truth table

| **Input** | **Output** | **Input** | **Output** | **Input** | **Output** | **Input** | **Output** | **Input** | **Output** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **c****lk_in0** | **clk_out0** | **c****lk_in****9****0** | **clk_out90** | **c****lk_in****18****0** | **clk_out180** | **c****lk_in****27****0** | **clk_out270** | **clksim_in** | **clksim_out** |
| 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| X | X | X | X | X | X | X | X | X | X |
| Z | Z | Z | Z | Z | Z | Z | Z | Z | Z |

Note: X = Unknown, Z = high Z

### Timing arcs

Figure 215 Clock buffer timing diagram

Table 222 Clock buffer 4-in-4-out timing arc

| Pin name | Direction | Related pin | Sdf cond | Timing type | Timing sense |
| --- | --- | --- | --- | --- | --- |
| **clk_out****0** | output | clk_in0 | NA | combinational | positive_unate |
| **clk_out****90** | output | clk_in90 | NA | combinational | positive_unate |
| **clk_out****18****0** | output | clk_in180 | NA | combinational | positive_unate |
| **clk_out****27****0** | output | clk_in270 | NA | combinational | positive_unate |
| **clk****sim****_out** | output | clksim_in | NA | combinational | positive_unate |

## Clock gater

### Overview

| # | Cell Name | Description |
| --- | --- | --- |
| 1 | dwc_ucie2phy_clkgt_a | Clock gater used in pclk in WRITE clock tree |
| 2 | dwc_ucie2phy_clkgt1_a | Clock gater used in cal_clk in WRITE clock tree |
| 3 | dwc_ucie2phy_clkgt2_a | Clock gater used in cal_clk in WRITE clock tree – x32 PHY config |

### Block diagram

Figure 216 Clock gater block diagram

### Pin description

Table 26 Clock gater pin description

| **No** | **Signal names** | **Direction** | **Type** | **Domain** | **Max frequency** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | SE | Input | Digital | VDD | - | Scan enable |
| 2 | EN | Input | Digital | VDD | - | Clock gate enable |
| 3 | CK | Input | Clock | VDD | 10 GHz | Input clock |
| 4 | Q | Output | Clock | VDD | 10 GHz | Output clock |
| 5 | VDD | Input | Power | VDD | - | Core power supply |
| 6 | VSS | input | Ground | VDD | - | Core ground |

### Operation waveform

The operation of clock gater is described in below waveform

Figure 217 Operation waveform of clock gater

### Timing arcs

Figure 218 Clock gater timing diagram

Table 28 Clock gater timing arc

| Pin name | Direction | Related pin | Sdf cond | Timing type | Timing sense |
| --- | --- | --- | --- | --- | --- |
| **CK** | input | CK | ENABLE_NOT_EN_AND_NOT_SE==1’b1 | min_pulse_width | NA |
| **CK** | input | CK | ENABLE_NOT_EN_AND_SE==1’b1 | min_pulse_width | NA |
| **CK** | input | CK | ENABLE_EN_AND_NOT_SE==1’b1 | min_pulse_width | NA |
| **CK** | input | CK | ENABLE_EN_AND_SE==1’b1 | min_pulse_width | NA |
| **EN** | input | CK | ENABLE_NOT_SE==1’b1 | setup_rising, hold_rising | NA |
| **SE** | input | CK | ENABLE_NOT_EN==1’b1 | setup_rising, hold_rising | NA |
| **Q** | output | CK | ENABLE_NOT_EN_AND_NOT_SE==1’b1 | combinational_fall | positive_unate |
| **Q** | output | CK | ENABLE_NOT_EN_AND_SE==1’b1 | combinational | positive_unate |
| **Q** | output | CK | ENABLE_EN_AND_NOT_SE==1’b1 | combinational | positive_unate |
| **Q** | output | CK | ENABLE_EN_AND_SE==1’b1 | combinational | positive_unate |

## Mux 2 to 1

### Overview

| # | Cell Name | Purpose |
| --- | --- | --- |
| 1 | dwc_ucie2phy_muxw2_a | mux in cal_clk in DW Write |

### Block diagram

Figure 219 Mux block diagram

Table 223 True table

| **S** | **D0** | **D1** | **Y** |
| --- | --- | --- | --- |
| **0** | 0 | X | 0 |
| **0** | 1 | X | 1 |
| **1** | X | 0 | 0 |
| **1** | X | 1 | 1 |

### Pin description

Table 224 Mux pin description

| **No** | **Signal names** | **Direction** | **Type** | **Domain** | **Max frequency** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | S | Input | Digital | VDD | - | Selection control |
| 2 | D0 | Input | Clock | VDD | 10 GHz | Input clock |
| 3 | D1 | Input | Clock | VDD | 10 GHz | Input clock |
| 4 | X | Output | Clock | VDD | 10 GHz | Output clock |
| 5 | VDD | Input | Power | VDD | - | Core power supply |
| 6 | VSS | input | Ground | VDD | - | Core ground |

### Timing arcs

Table 225 Mux 2-to-1 timing arc

| Pin name | Direction | Related pin | Sdf cond | Timing type | Timing sense |
| --- | --- | --- | --- | --- | --- |
| **X** | output | D0 | S===1'b0 | combinational | positive_unate |
| **X** | output | D1 | S===1'b1 | combinational | positive_unate |
| **X** | output | S | NA | combinational | positive_unate |
| **X** | output | S | NA | combinational | negative_unate |
| **D0** | input | NA | NA | NA | NA |
| **D1** | input | NA | NA | NA | NA |
| **S** | input | NA | NA | NA | NA |
| **VDD** | input | NA | NA | NA | NA |
| **VSS** | input | NA | NA | NA | NA |

### Timing arcs

Table 226 Mux 4-to-2 timing arcs

| Pin name | Direction | Related pin | Sdf cond | Timing type | Timing sense |
| --- | --- | --- | --- | --- | --- |
| **X****0** | output | D0 | S===1'b0 | combinational | positive_unate |
| **X****0** | output | D1 | S===1'b1 | combinational | positive_unate |
| **X****1** | output | D2 | S===1'b0 | combinational | positive_unate |
| **X****1** | output | D3 | S===1'b1 | combinational | positive_unate |
| **X0** | output | S | NA | combinational | positive_unate |
| **X0** | output | S | NA | combinational | negative_unate |
| **X1** | output | S | NA | combinational | positive_unate |
| **X1** | output | S | NA | combinational | negative_unate |
| **D0** | input | NA | NA | NA | NA |
| **D1** | input | NA | NA | NA | NA |
| **S** | input | NA | NA | NA | NA |
| **VDD** | input | NA | NA | NA | NA |
| **VSS** | input | NA | NA | NA | NA |

## Mux 4 to 2 in READ Clock tree

### Overview

| # | Cell Name | Purpose |
| --- | --- | --- |
| 1 | dwc_ucie2phy_muxr1_a | Repair mux – placed after RXCK |

### Block diagram

Figure 220 Mux 4 to 2 in READ Clock tree block diagram

Table 227 True table

| **S** | **D0** | D1 | **X****0** | D2 | D3 | X1 |
| --- | --- | --- | --- | --- | --- | --- |
| **0** | 0 | X | 0 | 0 | X | 0 |
| **0** | 1 | X | 1 | 1 | X | 1 |
| **1** | X | 0 | 0 | X | 0 | 0 |
| **1** | X | 1 | 1 | X | 1 | 1 |

### Pin description

Table 228 Mux pin description

| **No** | **Signal names** | **Direction** | **Type** | **Domain** | **Max frequency** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | S | Input | Digital | VDD | - | Selection control |
| 2 | D0 | Input | Clock | VDDREG | 10 GHz | Input clock |
| 3 | D1 | Input | Clock | VDDREG | 10 GHz | Input clock |
| 4 | X0 | Output | Clock | VDDREG | 10 GHz | Output clock |
| 5 | D2 | Input | Clock | VDDREG | 10 GHz | Input clock |
| 6 | D3 | Input | Clock | VDDREG | 10 GHz | Input clock |
| 7 | X1 | Output | Clock | VDDREG | 10 GHz | Output clock |
| 8 | VDD | Input | Power | VDD | - | Power supply |
| 9 | VDDREG | Input | Power | VDDREG | - | Power supply |
| 10 | VSS | input | Ground | VSS | - | Core ground |

### Timing arcs

Table 229 Mux 4-to-2 timing arcs

| Pin name | Direction | Related pin | Sdf cond | Timing type | Timing sense |
| --- | --- | --- | --- | --- | --- |
| **X****0** | output | D0 | S===1'b0 | combinational | positive_unate |
| **X****0** | output | D1 | S===1'b1 | combinational | positive_unate |
| **X****1** | output | D2 | S===1'b0 | combinational | positive_unate |
| **X****1** | output | D3 | S===1'b1 | combinational | positive_unate |
| **X****0** | output | S | NA | combinational | positive_unate |
| **X****0** | output | S | NA | combinational | negative_unate |
| **X1** | output | S | NA | combinational | positive_unate |
| **X1** | output | S | NA | combinational | negative_unate |
| **D0** | input | NA | NA | NA | NA |
| **D1** | input | NA | NA | NA | NA |
| **S** | input | NA | NA | NA | NA |
| **VDD** | input | NA | NA | NA | NA |
| **VDD****REG** | input | NA | NA | NA | NA |
| **VSS** | input | NA | NA | NA | NA |

## Clock load for WRITE clock tree

### Overview

**dwc_****ucie****phy_clkload** is used for tx loading of write clock tree for skew balance.

| # | Cell Name | Description |
| --- | --- | --- |
| 1 | dwc_ucie2phy_clkloadtx_a | Clock dummy load for balance loading for TX |
| 2 | dwc_ucie2phy_clkload1tx_a | Clock dummy load for balance loading for Txclk_CK |
| 3 | dwc_ucie2phy_clkload2tx_a | Clock dummy load for balance loading for Txclk_CK |

### Block diagram

Figure 221 Clock load for write clock tree diagram

### Pin description

Table 230 Clock load pin description

| **No** | **Signal names** | **Direction** | **Type** | **Domain** | **Max frequency** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | X_0 | Input | Clock | VDD | - | Input of dummy loading |
| 2 | X_90 | Input | Clock | VDD | - | Input of dummy loading |
| 3 | VDD | Input | Power | VDD | - | Core power supply |
| 4 | VSS | Input | Ground | VDD | - | Core ground |

## Clock load for read clock tree

### Overview

| # | Cell Name | Description |
| --- | --- | --- |
| 1 | dwc_ucie2phy_clkloadrx_a | Clock dummy load for balance loading for RX |

### Block diagram

Figure 222 Clock load for read clock tree diagram

### Pin description

Table 231 Clock load pin description

| **No** | **Signal names** | **Direction** | **Type** | **Domain** | **Max frequency** | **Description** |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | X_0 | Input | Clock | VDD | - | Input of dummy loading |
| 2 | X_90 | Input | Clock | VDD | - | Input of dummy loading |
| 3 | X_180 | Input | Clock | VDD | - | Input of dummy loading |
| 4 | X_270 | Input | Clock | VDD | - | Input of dummy loading |
| 5 | X_SIM | Input | Clock | VDD | - | Input of dummy loading |
| 6 | VDD | Input | Power | VDD | - | Core power supply |
| 7 | VSS | Input | Ground | VSS | - | Core ground |

# Clock Tree Architecture

## x64 - Write clock tree inside DWORD for Dec-TC

Figure 31 Write clock tree at DW x64 - TC version

## x64 - Write clock tree inside DWORD

Figure 32 Write clock tree at DW x64

## x32 - Write clock tree inside DWORD

Figure 33 Write clock tree at DW x32

## X64 - Read clock tree inside DWORD for Dec-TC

Figure 34 DW x64 Read clock tree - TC version

## x64 - Read clock tree inside DWORD

**Figure ****3****5**** ****DW**** x64**** ****Read clock tree**

Figure 36 DW x64 Read clock tree with SIM

Figure 37 DW x32 Read clock tree

Figure 38 DW x32 Read clock tree with SIM

## Clock tree inside MMPL

Table 31 Block diagram of MMPL clock tree

Clock buffer enable signal (clk_en[1:0]) is configurable by CSR and depends on PHY configuration:

| **No** | **clk_en[0]** | **clk_en[1]** | **Description** |
| --- | --- | --- | --- |
| 1 | 1 | 0 | PHY only has DW on LEFT side |
| 2 | 0 | 1 | PHY only has DW on RIGHT side |
| 3 | 1 | 1 | PHY has DW on both sides |

## Pclk in PHY TOP for Dec-TC

Table 32 Block diagram top PHY clock tree 8DWs both-side connection

## Pclk in PHY TOP

Figure 39 Block diagram top PHY clock tree 4DWs left-side/right-side/both-side connection

Figure 310 Block diagram top PHY clock tree 8DWs left-side connection

Figure 311 Block diagram top PHY clock tree 8DWs right-side connection

Figure 312 Block diagram top PHY clock tree full 16DWs connection

## Pre-mapped cells.

Below are pre-mapped cells used in the PHY:

| Premapped cells | H200 – SF4 | H201 – N5 |  |
| --- | --- | --- | --- |
| stdcell_wa_mux1 | HDBSLT04_MUX2_MMUCIE_4 |  |  |
| stdcell_wa_buf1 | HDBSLT04_BUF_SUCIE_12 |  |  |
| stdcell_wa_reg1 | HDBSLT04_SYNC6RMSFQ_Y2_1 |  |  |
| stdcells_ra_mux1 | HDBSLT04_MUX2_MMUCIE_4 |  |  |
| stdcells_ra_an1 | HDBSLT04_AN2_MMUCIE_4 |  |  |

## IDDQ Measurement Condition

Input clock must be parked at 0. For different clock input, they should be parked at differential low (clk is 0 and clk bar is 1). The “rfb_en” pin is also set 0 in IDDQ measurement mode.

## Burn-in Recommendation

To ensure maximum toggling of internal nodes during burn-in test, the recommendation is to run in mission mode.

If clock tree uses an internal voltage supply (Vreg), user need to keep Vreg level same as VDD core. To do this, voltage regulator is configured in bypass mode.

# Electrical Specification (TBU)

## Electrical specification

Table 41 Electrical specification of Write clock tree

| Item | Description | Specification | Final post-sim result | Unit |  |  |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  | Min | Typ | Max |  |
| Delay | Total delay from PLL output clock to TX DQ | 249-553 | 254 | - | 542.17 | ps |
| Skew | Delay skew b/w nearest DW and farthest DW whole PHY with MC | < 60 | 5.71 | - | 12.64 | ps |
|  | Delay skew b/w TX DQ without MC | 3.4 | - | - | 3.35 | ps |
|  | Delay skew b/w TX DQ with MC | < 10 | - | - | 8.35 | ps |
|  | Delay skew b/w DQ and DQS with MC | ±20 | -10.64 | - | 15.5 | ps |
| Duty Cycle | DCD distribution from PLL output to DCD | ±5 | -7.28 | - | 13.73 | % |
| Aging | DCD distribution from PLL output to DWDCD (10yrs, stress VDDnom+5%) | -15 | -7 | - | 12.3 | % |
|  | Delay shift (10yrs, stress VDDnom+5%) | 237 | 253.98 | - | 561.65 | ps |
| Slew(transition time) | Slew at TX DQ (10%-90%) | < 22 | - | - | 20.8 | ps |
|  | Worst Case Slew inside PHY CLKTREE (10%-90%) | < 35 | - | - | 32. 57 | ps |
| Power supply jitter | Measure at TX DQ by changing supply 5%Vsup | 1.23 | - | - | 1.23 | ps/mV |
|  | Power supply jitter convert | 5.77 | - | - | 5.77 | ps/mV |
| Power Consumption | Average current consumption, TT_0.75V_25C, 8GHz clock, whole DW | 41.9 | - | 41.9 | - | mA |
|  | Average current consumption, TT_0.75V_25C, 8GHz clock, whole PHY | 40.9 | - | 40.9 | - | mA |

Table 42 Electrical specification of Read clock tree

| Item | Description | Specification | Final post-sim result | Unit |  |  |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  | Min | Typ | Max |  |
| Delay | Total delay from DLL output clock to RX DQ | 87-195 | 88.8 | - | 191.4 | ps |
| Skew | Delay skew b/w RX DQ, PVT sim | 6.4 | - | - | 6.40 | ps |
|  | Delay skew b/w RX DQ, Monte Carlo simulation | < 10 | - | - | 9.54 | ps |
| DCD | DCD at RX DQ, input clk DCD = 50%-50% | ±5 | -4.12 | - | 4.77 | % |
|  | DCD at RX DQ, Monte Carlo simulation | ±8 | -7.82 | - | 6.85 | % |
| Aging | DCD absolutely shift (10yrs, stress VDDnom+5%) | < 0.5 | - | - | 0.43 | % |
|  | Delay shift (10yrs, stress VDDnom+5%) | < 5 | - | - | 4.1 | % |
| Slew | Slew at RX DQ (10%-90%) | < 22 | - | - | 20.2 | ps |
|  | Worst Case Slew (10%-90%) | < 35 | - | - | 34.3 | ps |
| Power supply jitter | Measure at RX DQ by changing supply 5%Vsup | 0.38 | - | - | 0.38 | ps/mV |
|  | Power supply jitter convert | 1.8 | - | - | 1.77 | ps |
| Power Consumption | Average current consumption, TT_0.75V_25C, 8GHz clock, whole PHY | 35 | - | 34.66 | - | mA |

## Power consumption

Table 43 Current consumption in different PHY TOP operation mode

| Cell Name | Power Mode​ | Description​ | Power domain | Spec | TT-0.75v-25c | FF_0.935v_125c​ | Unit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dwc_uciephy_clktx | Active | VDD valid, clock toggle, real load from full clock tree path | VDD | -​ | 7.14 | 9.73 | mA |
|  | LP2 | VDD valid, data and clock static | VDD | -​ | 3.60 | 240 | uA |
| dwc_uciephy_clkrx | Active | VDD valid, clock toggle, real load from full clock tree path | VDD | -​ | 0.61 | 0.84 | mA |
|  | LP2 | VDD valid, clock static | VDD | -​ | 0.33 | 22.2 | uA |
| dwc_uciephy_clkrpt | Active | VDD valid, clock toggle, real load from full clock tree path | VDD | -​ | 3.14 | 4.28 | mA |
|  | LP2 | VDD valid, clock static | VDD | -​ | 1.53 | 101 | uA |
| dwc_uciephy_clkrpt1 | Active | VDD valid, clock toggle, real load from full clock tree path | VDD | -​ | 1.91 | 2.42 | mA |
|  | LP2 | VDD valid, clock static | VDD | -​ | 0.97 | 64.4 | uA |
| dwc_uciephy_clktx2 | Active | VDD valid, clock toggle, real load from full clock tree path | VDD | -​ | 16.07 | 21.89 | mA |
|  | LP2 | VDD valid, clock static | VDD | -​ | 8.1 | 540 | uA |

## EMIR condition

Table 44 EMIR verification condition

| Process | VDD | Temp | RC Corner | Operation mode |
| --- | --- | --- | --- | --- |
| **FF** | 0.935 | 105 | typical | Full path clock tree, toggle clock input with the frequency as below: 8GHz for write clock 8GHz for read clock |
| **SS** | 0.668 | 105 | typical |  |

Verification flow: CustomSim RA with Self-heating effect (SHE)

# Verification List

## bbSim verification list (TBU)

Table 51 Verification list

| Vector name | Test case / cell name | Description |
| --- | --- | --- |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
