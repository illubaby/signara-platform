**DesignWareCore ****UCIE**** PHY**

Data book

UCIE2PHY Clock Tree for Standard package

dwc_ucie2phy_clktree

Version 0.7

Jan 30, 2026

Copyright Notice and Proprietary Information Notice

Copyright © 2024 Synopsys, Inc. All rights reserved. This software and documentation contain confidential and proprietary information that is the property of Synopsys, Inc. The software and documentation are furnished under a license agreement and may be used or copied only in accordance with the terms of the license agreement. No part of the software and documentation may be reproduced, transmitted, or translated, in any form or by any means, electronic, mechanical, manual, optical, or otherwise, without prior written permission of Synopsys, Inc., or as expressly provided by the license agreement.

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
| **Sep 10, 2024** | Dao Tran | 0.1 | Initial version |
| **Oct 14, 2024** | Dao Tran | 0.11 | Update section 3.1 X16 Write clock tree Add POR and add RxClkOut mux for Track path Update section 3.2 X16 Read clock tree Remove one DCD and update DCD location. |
| **Oct 17, 2024** | Dao Tran | 0.12 | Follow the jira To solve the unstable output clock of PhaseGen. Add new loading cell for delay skew blalancing between TxClk_DATA and TxClk_CK: dwc_ucie2phy_clkload1_tx Update section 3.1 X64 – Write clock tree : Update Loading cell connection. |
| **Oct 28, 2024** | Dao Tran | 0.13 | Update section 3.1 X16 Write clock tree Add custom connection for TXCKP/CKN RXCKP/CKN loopback support. |
| **Nov 08, 2024** | Dao Tran | 0.14 | Update section 3.2 X64 – Write clock tree: update connections of input Muxwa1. Add AND pre-map loadings for the RxClkOut paths, that follow latest Arch-Spec Update section 3.4 X64 – Read clock tree: remove pre-map loadings, that follow latest Arch-Spec To avoid confusion, detail updates will be clarified on the Jira |
| **Nov 27, 2024** | Dao Tran | 0.15 | Update name of all the used cells from *w/ra* to *w/rs* to separate the cells list for advanced package and standard package. |
| **Dec 10, 2024** | Dao Tran | 0.16 | Update section 0 X16 - Read clock tree inside DWORD Replace one rx_load cell connection by RX_CAL cell connection at RXs group VREG3 |
| **Apr 11, 2025** | Tri Vo | 0.2 | Change cell name following new conventional name (UCIe-A/S and PHY orientation) |
| **Apr 13, 2025** | Dao Tran | 0.21 | Update The sections Clock Tree Architecture for consistency new cell name update |
| **Apr 1****7****, 2025** | Dao Tran | 0.22 | Add sections for DWORD-X32 clktree scheme 3.1 X32 - clock tree inside DWORD 3.4 Pclk in PHY TOP – X32 |
| **May 5, 2025** | Quynh Tong | 0.23 | Update section 3.1 X16 – Write clock tree inside DWORD Add/remove tx_load cells in IO groups for consistency in loading in each group |

| **May ****9****, 2025** | Quynh Tong | 0.24 | Update cell list – Add new cell: dwc_ucie2phy_clkbufphy7_s Change cell name following new conventional name (remove PHY orientation _ns/ew) |
| --- | --- | --- | --- |
| **May 16, 2025** | Quynh Tong | 0.25 | Change cell name following new conventional name: remove _s for cells dwc_ucie2phy_dca/dcd/lcdl/por/tx_cal/vreg* Update PClk* pin names in PHYTOP – X32 |
| **Jun 10, 2025** | Tri Vo | 0.3 | Update write clock tree x32 to support AMZN config Separate PClkIn to PClkIn[1:0] Separate PClkBufIn/PClkBufOut to PClkBufIn[1:0]/PClkBufOut[1:0] Separate PClkBufIn1/PClkBufOut1 to PClkBufIn1[1:0]/PClkBufOut1[1:0] Read clock buffer: change VDD to VDDREG |
| **Jul 04, 2025** | Tri Vo | 0.35 | Add clock tree diagram of custom x16 AMNZ configuration Update diagram of custom x32 AMNZ configuration Swap PCLK[0] & [1] |
| **Jul 12, 2025** | Tri Vo | 0.4 | Update clkbufr1/2/3: add new pin clksim_in/out to support SIM Update clkrxload: Add new pin X_SIM to support SIM Change VDDREG to VDD Add new DW read clock tree with SIM |
| **Jul 19, 2025** | Tri Vo | 0.41 | Update clock buffer in MMPL. Now one MMPL supports both x16 and x32 configuration. dwc_ucie2phy_clkbufphyw7_s is no long supported () |
| **Oct 29, 2025** | Tri Vo | 0.5 | Clock for DFT: replace buffer by OCC mux to optimize timing (P80001562-800327) Loopback connection: support connection from TXTRK and TXCKRD to RXTRK and RXCKRD Correct diagram 3-10: swap connection pclkin[0] vs pclkin[1] () |
| **Nov 17, 2025** | Tri Vo | 0.55 | clkbufphyw1_a: add pin clk_en () Add section 3.2 describing the MMPL clock tree with enable signal |
| **Nov 27, 2025** | Tri Vo | 0.56 | Update read clock tree with SIM () |
| **Dec 29, 2025** | Tri Vo | 0.6 | Remove Clock mux for Track TX () New buffer dwc_ucie2phy_clkbufw11_s (replace muxw1_s) New dummy load dwc_ucie2phy_clkload2tx_s (similar to UCIe-A) Update Write clock tree x16 and x32 |
| **Jan 11, 2026** | Tri Vo | 0.61 | New buffer dwc_ucie2phy_lclkbuf_s |
| **Jan 30, 2026** | Tri Vo | 0.7 | New buffer dwc_ucie2phy_lclkbuf1_s () Add spec for lclkbuf* |

Reference Documents

# Introduction

## Overview

This Databook describes the information of clock buffer library for UCIe2 PHY, including design feature, electrical specification and clock tree integration guideline.

This library provides the set of clock buffers and clock gating that optimized for high speed clock distribution, low latency, skew and jitter requirement.

## Design features

Supports x16/x32 config, 16TX/32TX, 16RX/32RX

Maximum clock frequency: 10GHz

## Cell list

Table 11 - Cell list

| **#** | **Cell name** | **Description** |
| --- | --- | --- |
| 1 | dwc_ucie2phy_clkbufr1_s | Read Clock tree buffer 2-in-2-out: drive longest vertical route |
| 2 | dwc_ucie2phy_clkbufr2_s | Read Clock tree buffer 2-in-2-out: placed at each group |
| 3 | dwc_ucie2phy_clkbufr3_s | Read Clock tree buffer 4-in-4-out: last stage buffer |
| 4 | dwc_ucie2phy_clkbufw1_s | DW Write Clock tree buffer – input DW |
| 5 | dwc_ucie2phy_clkbufw2_s | DW Write Clock tree buffer 2-in-2-out – placed after Phase gen |
| 6 | dwc_ucie2phy_clkbufw3_s | DW Write Clock tree buffer 2-in-2-out – placed at each IO row |
| 7 | dwc_ucie2phy_clkbufw11_s | DW Write Clock tree buffer 2-in-2-out – placed at each group |
| 8 | dwc_ucie2phy_clkgt_s | DW Write Clock tree clock gate for pclk |
| 9 | dwc_ucie2phy_clkgt1_s | DW Write Clock tree clock gate for cal_clk |
| 10 | dwc_ucie2phy_muxw2_s | DW Write Clock tree mux for cal_clk |
| 11 | dwc_ucie2phy_clkbufphyw1_s | PHYTOP Clock tree buffer – placed in MMPL |
| 12 | dwc_ucie2phy_clkbufphyw2_s | PHYTOP Clock tree buffer – placed in DW |
| 13 | dwc_ucie2phy_clkbufphyw3_s | PHYTOP Clock tree buffer – placed in MMPL for PLL isolate load |
| 14 | dwc_ucie2phy_clkbufphyw4_s | PHYTOP Clock tree buffer – placed in DW |
| 15 | dwc_ucie2phy_clkloadrx_s | Dummy load IO RX |
| 16 | dwc_ucie2phy_clkloadtx_s | Dummy load IO TX |
| 17 | dwc_ucie2phy_clkload1tx_s | Dummy load for TxClk_CK (horizontal wire) |
| 18 | dwc_ucie2phy_clkload1tx_s | Dummy load for TxClk_CK (vertical wire) |
| 19 | dwc_ucie2phy_clkbufphyw5_s | PHYTOP Clock tree buffer – placed in DW |
| 20 | dwc_ucie2phy_clkbufphyw6_s | PHYTOP Clock tree buffer – placed in DW |
| 21 | dwc_ucie2phy_lclkbuf_a | LCLK buffer. DI uses this buffer to build LCLK tree |
| 22 | dwc_ucie2phy_lclkbuf1_a | LCLK buffer. DI uses this buffer to build LCLK tree |

# Functional Description

## Clock buffer

Figure 21 Clock buffer cell list

| # | Cell name | Description |
| --- | --- | --- |
| 1 | dwc_ucie2phy_clkbufphyw1_s | PHYTOP Clock tree buffer – placed in MMPL |
| 2 | dwc_ucie2phy_clkbufphyw2_s | PHYTOP Clock tree buffer – placed in DW |
| 3 | dwc_ucie2phy_clkbufphyw3_s | PHYTOP Clock tree buffer – placed in MMPL for PLL isolate load |
| 4 | dwc_ucie2phy_clkbufphyw4_s | PHYTOP Clock tree buffer – placed in DW |
| 5 | dwc_ucie2phy_clkbufphyw5_s | PHYTOP Clock tree buffer – placed in DW |
| 6 | dwc_ucie2phy_clkbufphyw6_s | PHYTOP Clock tree buffer – placed in DW |
| 7 | dwc_ucie2phy_lclkbuf_s | LCLK buffer. DI uses this buffer to build LCLK tree |
| 8 | dwc_ucie2phy_lclkbuf1_s | LCLK buffer. DI uses this buffer to build LCLK tree |

### Block diagram

Figure 22 Block diagram of clkbufphyw1_s

Table 21 Block diagram of clkbufphyw2/3/4/5/6_s and lclkbuf_s/lclkbuf1_s

### Pin description

Table 22 Pin description of clkbufphyw1_a

| No | Signal names | Direction | Type | Domain | Max frequency | Description |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | clk_in | Input | Clock | VDD | 2 to 10 GHz | Input of buffer |
| 2 | clk_en | Input | Digital | VDD | - | Asynchronous enable. |
| 3 | clk_out | Output | Clock | VDD | 2 to 10 GHz | Output of buffer |
| 4 | VDD | Input | Power | VDD | - | Core power supply |
| 5 | VSS | input | Ground | VDD | - | Core ground |

Table 23 Pin description of clkbufphyw2/3/4/5/6_a

| No | Signal names | Direction | Type | Domain | Max frequency | Description |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | clk_in | Input | Clock | VDD | 2 to 10 GHz | Input of buffer |
| 2 | clk_out | Output | Clock | VDD | 2 to 10 GHz | Output of buffer |
| 3 | VDD | Input | Power | VDD | - | Core power supply |
| 4 | VSS | input | Ground | VDD | - | Core ground |

Table 24 Pin description of lclkbuf_s and lclkbuf1_s

| No | Signal names | Direction | Type | Domain | Max frequency | Description |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | clk_in | Input | Clock | VDD | 2.5 GHz | Input of buffer |
| 2 | clk_out | Output | Clock | VDD | 2.5 GHz | Output of buffer |
| 3 | VDD | Input | Power | VDD | - | Core power supply |
| 4 | VSS | input | Ground | VDD | - | Core ground |

### Truth table

Table 25 Truth table of clkbufphyw1_a

| **clk_en** | **c****lk_in** | **c****lk_out** |
| --- | --- | --- |
| 0 | X | 0 |
| 0 | Z | 0 |
| 1 | 0 | 0 |
| 1 | 1 | 1 |
| 1 | X | X |
| 1 | Z | Z |

Table 26 Truth table of clkbufphyw2/3/4/5/6_a

| **Clk_in** | **Clk_out** |
| --- | --- |
| 0 | 0 |
| 1 | 1 |
| X | X |
| Z | Z |

Note: X = Unknown, Z = high Z

**Timing arcs**

Figure 23 Clock buffer timing diagram

Table 27 Clock buffer timing arc

| Pin name | Direction | Related pin | Sdf cond | Timing type | Timing sense |
| --- | --- | --- | --- | --- | --- |
| **clk_out**** (*)** | output | clk_en | NA | combinational | nonunate |
| **clk_out** | output | clk_in | NA | combinational | positive_unate |

(*) Only available in clkbufphyw1_s

### LCLKBUF Specification

LCLKBUF* are custom buffers that PnR uses to build the clock tree for LCLK. The general specification:

Table 28 LCLKBUF specification

| Pin name | Direction | Cell name | Min | Typ | Max | Unit |
| --- | --- | --- | --- | --- | --- | --- |
| Fmax | Max input frequency | lclkbuf* |  |  | 2.5 | GHz |
| **Cmax** | Max loading | lclkbuf |  |  | 1 | pF |
|  |  | lclkbuf1 |  |  | 0.5 | pF |
| **Trf** | Transition time (10-90%VDD) | lclkbuf* |  |  | 50 | ps |
| **DCD** | Duty cycle distortion | lclkbuf* | -5 |  | +5 | % |

## Clock buffer with R feedback

### Overview

Figure 24 Clock buffer cell list

| **#** | **Cell name** | **Description** |
| --- | --- | --- |
| 1 | dwc_ucie2phy_clkbufw1_s | DW WRITE Clock tree buffer – input DW |

### Block diagram

Figure 25 Clock buffer block diagram

### Pin description

Table 29 Clock buffer pin description

| No | Signal names | Direction | Type | Domain | Max frequency | Description |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | clk_in | Input | Clock | VDD | 2 to 10 GHz | Input of buffer, 10GHz for RX clkpath for TX clkpath |
| 2 | clk_out | Output | Clock | VDD | 2 to 10 GHz | Output of buffer, 10GHz for RX clkpath and for TX clkpath |
| 3 | rfb_en | Input | Digital | VDD | - | Resistive Feedback enable for high frequency operation 1: Enable resistive feedback. (Freq range 8Ghz - 10Ghz) 0: Disable resistive feedback. (Freq range 2Ghz - <8Ghz) Set to 0 if the input clock is static/off (idle state/LP mode). |
| 4 | VDD | Input | Power | VDD | - | Core power supply |
| 5 | VSS | input | Ground | VSS | - | Core ground |

### Truth table

Table 210 Clock buffer truth table

| **Clk_in** | **Clk_out** |
| --- | --- |
| 0 | 0 |
| 1 | 1 |
| X | X |
| Z | Z |

Note: X = Unknown, Z = high Z

### Timing arcs

Figure 26 Clock buffer timing diagram

Table 211 Clock buffer timing arc

| Pin name | Direction | Related pin | Sdf cond | Timing type | Timing sense |
| --- | --- | --- | --- | --- | --- |
| **clk_out** | output | clk_in | NA | combinational | positive_unate |

## Clock buffer 2-in-2-out in WRITE Clock tree

### Overview

| **#** | **Cell name** | **Description** |
| --- | --- | --- |
| 1 | dwc_ucie2phy_clkbufw2_s | DW Write Clock tree buffer 2-in-2-out – placed after Phase gen |
| 2 | dwc_ucie2phy_clkbufw3_s | DW Write Clock tree buffer 2-in-2-out – placed at each TX row |
| 3 | dwc_ucie2phy_clkbufw11_s | DW Write Clock tree buffer 2-in-2-out – placed at each group |

### Block diagram

Figure 27 Clock buffer 2-in-2-out in WRITE Clock tree block diagram

### Pin description

Table 212 Clock buffer pin 2-in-2-out in WRITE Clock tree description

| No | Signal name | Direction | Type | Domain | Max frequency | Description |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | clk_in0 | Input | Clock | VDD | 2 to 10 GHz | Input of buffer |
| 2 | clk_in90 | Input | Clock | VDD | 2 to 10 GHz | Input of buffer |
| 3 | clk_out0 | Output | Clock | VDD | 2 to 10 GHz | Output of buffer |
| 4 | clk_out90 | Output | Clock | VDD | 2 to 10 GHz | Output of buffer |
| 5 | VDD | Input | Power | VDD | - | Core power supply |
| 6 | VSS | input | Ground | VSS | - | Core ground |

### Truth table

Table 213 Clock buffer 2-in-2-out in READ Clock tree truth table

| **Clk_in0** | **Clk_in90** | **Clk_out0** | **Clk_out90** |
| --- | --- | --- | --- |
| 0 | 0 | 0 | 0 |
| 1 | 1 | 1 | 1 |
| X | X | X | X |
| Z | Z | Z | Z |

Note: X = Unknown, Z = high Z

### Timing arcs

Figure 28 Clock buffer timing diagram

Table 214 Clock buffer 2-in-2-out in WRITE Clock tree timing arc

| Pin name | Direction | Related pin | Sdf cond | Timing type | Timing sense |
| --- | --- | --- | --- | --- | --- |
| **clk_out****0** | output | clk_in0 | NA | combinational | positive_unate |
| **clk_out90** | output | clk_in90 | NA | combinational | positive_unate |

## Clock buffer 3-in-3-out in READ Clock tree

### Overview

| **#** | **Cell name** | **Description** |
| --- | --- | --- |
| 1 | dwc_ucie2phy_clkbufr2_s | Read Clock tree buffer 3-in-3-out: placed at each group |

### Block diagram

Figure 29 Clock buffer 3-in-3-out in READ Clock tree block diagram

### Pin description

Table 215 Clock buffer pin 3-in-3-out in READ Clock tree description

| No | Signal name | Direction | Type | Domain | Max frequency | Description |
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

Table 216 Clock buffer 3-in-3-out in READ Clock tree truth table

| **Input** | **Output** | **Input** | **Output** | **Input** | **Output** |
| --- | --- | --- | --- | --- | --- |
| **clk_in** | **clk_out** | **clk_in_b** | **clk_out_b** | **clksim_in** | **clksim_out** |
| 0 | 0 | 0 | 0 | 0 | 0 |
| 1 | 1 | 1 | 1 | 1 | 1 |
| X | X | X | X | X | X |
| Z | Z | Z | Z | Z | Z |

Note: X = Unknown, Z = high Z

### Timing arcs

Figure 210 Clock buffer timing diagram

Table 217 Clock buffer timing arc

| Pin name | Direction | Related pin | Sdf cond | Timing type | Timing sense |
| --- | --- | --- | --- | --- | --- |
| **clk_out** | output | clk_in | NA | combinational | positive_unate |
| **clk_out_b** | output | clk_in_b | NA | combinational | positive_unate |
| **clk****sim****_out** | output | clksim_in | NA | combinational | positive_unate |

## Clock buffer 3-in-3-out in READ Clock tree with R Feedback

### Overview

| **#** | **Cell name** | **Description** |
| --- | --- | --- |
| 1 | dwc_ucie2phy_clkbufr1_s | Read Clock tree buffer 3-in-3-out: drive longest vertical route |

### Block diagram

Figure 211 Clock buffer 3-in-3-out in READ Clock tree block diagram

### Pin description

Table 218 Clock buffer pin 3-in-3-out in READ Clock tree description

| No | Signal name | Direction | Type | Domain | Max frequency | Description |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | clk_in | Input | Clock | VDDREG | 2 to 10 GHz | Input of buffer |
| 2 | clk_in_b | Input | Clock | VDDREG | 2 to 10 GHz | Input of buffer |
| 3 | clksim_in | Input | Clock | VDDREG | 2 to 10 GHz | SIM clock input |
| 4 | clk_out | Output | Clock | VDDREG | 2 to 10 GHz | Output of buffer |
| 5 | clk_out_b | Output | Clock | VDDREG | 2 to 10 GHz | Output of buffer |
| 6 | clksim_in | Input | Clock | VDDREG | 2 to 10 GHz | SIM clock output |
| 7 | rfb_en | Input | Digital | VDD | - | Resistive Feedback enable for high frequency operation 1: Enable resistive feedback. (Freq range 8Ghz - 10Ghz) 0: Disable resistive feedback.(Freq range 2Ghz - <8Ghz) Set to 0 if the input clock is static/off (idle state/LP mode). |
| 8 | VDD | Input | Power | VDD | - | Power supply |
| 9 | VDDREG | Input | Power | VDDREG |  | Power supply |
| 10 | VSS | input | Ground | VDDREG | - | Core ground |

### Truth table

Table 219 Clock buffer 3-in-3-out in READ Clock tree truth table

| **Input** | **Output** | **Input** | **Output** | **Input** | **Output** |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **clk_in** | **rfb_en** | **clk_out** | **clk_in_b** | **rfb_en** | **clk_out_b** | **clksim_in** | **rfb_en** | **clksim_out** |
| 0 | 0/1 | 0 | 0 | 0/1 | 0 | 0 | 0/1 | 0 |
| 1 | 0/1 | 1 | 1 | 0/1 | 1 | 1 | 0/1 | 1 |
| X | 0/1 | X | X | 0/1 | X | X | 0/1 | X |
| Z | 0/1 | Z | Z | 0/1 | Z | Z | 0/1 | Z |

Note: X = Unknown, Z = high Z

### Timing arcs

Figure 212 Clock buffer timing diagram

Table 220 Clock buffer timing arc

| Pin name | Direction | Related pin | Sdf cond | Timing type | Timing sense |
| --- | --- | --- | --- | --- | --- |
| **clk_out** | output | clk_in | NA | combinational | positive_unate |
| **clk_out_b** | output | clk_in_b | NA | combinational | positive_unate |
| **clk****sim****_out** | output | clksim_in | NA | combinational | positive_unate |

## Clock buffer 5-in-5-out in READ Clock tree

### Overview

| **#** | **Cell name** | **Description** |
| --- | --- | --- |
| 1 | dwc_ucie2phy_clkbufr3_s | Read Clock tree buffer 5-in-5-out: drive longest vertical route |

### Block diagram

Figure 213 Clock buffer 5-in-5-out in READ Clock tree block diagram

### Pin description

Table 221 Clock buffer pin 4-in-4-out in READ Clock tree description

| No | Signal name | Direction | Type | Domain | Max frequency | Description |
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

Table 222 Clock buffer truth table

| **Input** | **Output** | **Input** | **Output** | **Input** | **Output** | **Input** | **Output** | **Input** | **Output** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **c****lk_in0** | **clk_out0** | **c****lk_in****9****0** | **clk_out90** | **c****lk_in****18****0** | **clk_out180** | **c****lk_in****27****0** | **clk_out270** | **clksim_in** | **clksim_out** |
| 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| X | X | X | X | X | X | X | X | X | X |
| Z | Z | Z | Z | Z | Z | Z | Z | Z | Z |

Note: X = Unknown, Z = high Z

### Timing arcs

Figure 214 Clock buffer timing diagram

Table 223 Clock buffer 4-in-4-out timing arc

| Pin name | Direction | Related pin | Sdf cond | Timing type | Timing sense |
| --- | --- | --- | --- | --- | --- |
| **clk_out****0** | output | clk_in0 | NA | combinational | positive_unate |
| **clk_out****90** | output | clk_in90 | NA | combinational | positive_unate |
| **clk_out180** | output | clk_in180 | NA | combinational | positive_unate |
| **clk_out270** | output | clk_in270 | NA | combinational | positive_unate |
| **clk****sim****_out** | output | clksim_in | NA | combinational | positive_unate |

## Clock gater

### Overview

| # | Cell Name | Description |
| --- | --- | --- |
| 1 | dwc_ucie2phy_clkgt_s | Clock gater used in pclk in WRITE clock tree |
| 2 | dwc_ucie2phy_clkgt1_s | Clock gater used in cal_clk in WRITE clock tree |

### Block diagram

Figure 215 Clock gater block diagram

### Pin description

Table 26 Clock gater pin description

| No | Signal names | Direction | Type | Domain | Max frequency | Description |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | SE | Input | Digital | VDD | - | Scan enable |
| 2 | EN | Input | Digital | VDD | - | Clock gate enable |
| 3 | CK | Input | Clock | VDD | 10 GHz | Input clock |
| 4 | Q | Output | Clock | VDD | 10 GHz | Output clock |
| 5 | VDD | Input | Power | VDD | - | Core power supply |
| 6 | VSS | input | Ground | VDD | - | Core ground |

### Operation waveform

The operation of clock gater is described in below waveform

Figure 216 Operation waveform of clock gater

### Timing arcs

Figure 217 Clock gater timing diagram

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
| 1 | dwc_ucie2phy_muxw2_s | mux in cal_clk in DW Write |

### Block diagram

Figure 218 Mux block diagram

Table 224 True table

| S | D0 | D1 | Y |
| --- | --- | --- | --- |
| **0** | 0 | X | 0 |
| **0** | 1 | X | 1 |
| **1** | X | 0 | 0 |
| **1** | X | 1 | 1 |

### Pin description

Table 225 Mux pin description

| No | Signal names | Direction | Type | Domain | Max frequency | Description |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | S | Input | Digital | VDD | - | Selection control |
| 2 | D0 | Input | Digital | VDD | 10 GHz | Input clock |
| 3 | D1 | Input | Digital | VDD | 10 GHz | Input clock |
| 4 | X | Output | Digital | VDD | 10 GHz | Output clock |
| 5 | VDD | Input | Power | VDD | - | Core power supply |
| 6 | VSS | input | Ground | VDD | - | Core ground |

### Timing arcs

Table 226 Mux 2-to-1 timing arc

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

## Clock load for WRITE clock tree

### Overview

**dwc_****ucie****phy_clkload** is used for tx loading of write clock tree for skew balance.

| # | Cell Name | Description |
| --- | --- | --- |
| 1 | dwc_ucie2phy_clkloadtx_s | Clock dummy load for balance loading for TX |
| 2 | dwc_ucie2phy_clkload1tx_s | Clock dummy load for balance loading for TxClk_CK (horizontal wire) |
| 3 | dwc_ucie2phy_clkload2tx_s | Clock dummy load for balance loading for TxClk_CK (vertical wire) |

### Block diagram

Figure 219 Clock load for write clock tree diagram

### Pin description

Table 227 Clock load pin description

| No | Signal names | Direction | Type | Domain | Max frequency | Description |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | X_0 | Input | Clock | VDD | - | Input of dummy loading |
| 2 | X_90 | Input | Clock | VDD | - | Input of dummy loading |
| 3 | VDD | Input | Power | VDD | - | Core power supply |
| 4 | VSS | Input | Ground | VDD | - | Core ground |

## Clock load for read clock tree

### Overview

| # | Cell Name | Description |
| --- | --- | --- |
| 1 | dwc_ucie2phy_clkloadrx_s | Clock dummy load for balance loading for RX |

### Block diagram

Figure 220 Clock load for read clock tree diagram

### Pin description

Table 228 Clock load pin description

| No | Signal names | Direction | Type | Domain | Max frequency | Description |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | X_0 | Input | Clock | VDD | - | Input of dummy loading |
| 2 | X_90 | Input | Clock | VDD | - | Input of dummy loading |
| 3 | X_180 | Input | Clock | VDD | - | Input of dummy loading |
| 4 | X_270 | Input | Clock | VDD | - | Input of dummy loading |
| 5 | X_SIM | Input | Clock | VDD | - | Input of dummy loading |
| 6 | VDD | Input | Power | VDD | - | Core power supply |
| 7 | VSS | Input | Ground | VSS | - | Core ground |

# Clock Tree Architecture

## X16 - Write clock tree inside DWORD

Figure 31 Write clock tree at DW level

## X16 - Read clock tree inside DWORD

Figure 32 DW Read clock tree

Figure 33 DW Read clock tree with SIM

## X32 - clock tree inside DWORD

## Clock tree inside MMPL

Table 31 Block diagram of MMPL clock tree

Clock buffer enable signal (clk_en[1:0]) is configurable by CSR and depends on PHY configuration:

| No | clk_en[0] | clk_en[1] | Description |
| --- | --- | --- | --- |
| 1 | 1 | 0 | PHY only has DW on LEFT side |
| 2 | 0 | 1 | PHY only has DW on RIGHT side |
| 3 | 1 | 1 | PHY has DW on both sides |

## Pclk in PHY TOP – X16

Figure 34 Block diagram top PHY clock tree 2sides 4DWs/2DWs connection

Figure 35 Block diagram top PHY clock tree 4DWs left/right-side connection

Figure 36 Block diagram top PHY clock tree full 8DWs connection

Figure 37 Custom AMNZ x16 configuration

## Pclk in PHY TOP – X32

Figure 38 Block diagram top PHY clock tree-X32 2sides 4DWs

Figure 39 Block diagram top PHY clock tree-X32 2sides 2DWs

Figure 310 Custom AMNZ x32 configuration

## Premapped cells.

Below are premapped cells using in the PHY:

| Premapped cells | SF4 | N5 |  |
| --- | --- | --- | --- |
| stdcell_ws_mux1 | HDBSLT04_MUX2_MMUCIE_4 |  |  |
| stdcell_ws_buf1 | HDBSLT04_BUF_SUCIE_12 |  |  |
| stdcell_ws_reg1 | HDBSLT04_SYNC6RMSFQ_Y2_1 |  |  |
| stdcells_rs_mux1 | HDBSLT04_MUX2_MMUCIE_4 |  |  |
| stdcells_rs_an1 | HDBSLT04_AN2_MMUCIE_4 |  |  |
| stdcell_wa_occmux |  |  |  |

## IDDQ Measurement Condition

Input clock must be parked at 0. For different clock input, they should be parked at differential low (clk is 0 and clk bar is 1).

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
