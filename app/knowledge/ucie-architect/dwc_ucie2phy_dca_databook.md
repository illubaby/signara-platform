**DesignWareCore ****UCIe**** ****2****.0**** PHY**

Data book

UCIe 2.0 PHY Duty Cycle Adjustment

dwc_ucie2phy_dca

May 09, 2025

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

| Date | Owner | Revision | Approve by | Description |
| --- | --- | --- | --- | --- |
| **Apr 26, 2024** | DaoTran | 0.1 | Tri Vo | 1. Clone from Ucie1.0 PHY dwc_uciephy_dca 2. Remove one DCA_core stage in the architecture. Update Pinlist Update Figure 11 - DCA block diagram Update Figure 12 - Core DCA block diagram Update section 4.2: DCA calibration |
| **Dec 19, 2024** | DaoTran | 0.11 | Tri Vo | Add sections 4.3 DFT Mode, 4.4 IDDQ Measurement, 4.5 Burn-in Mode Update Table 21, Table 22 due to the update in default mode operation. |
| **Apr 11, 2025** | Tri Vo | 0.2 | Tri Vo | Change cell name following new conventional name (UCIe-A/S, NS/EW PHY orientation) Format document |
| **May 09 2025** | Tri Vo | 0.21 | Tri Vo | Remove _a/s and _ns/ew in cell name |

Reference Documents

# Introduction

## Overview

In UCIe2.0, DCA block is used for adjusting duty cycle of write clock distribution. DCA acquires core VDD level clock signals, conditions them to adjust edge rates and duty cycle and drives them to digital circuits, DCA and IO driver blocks. DCA is a non-inverting block.

## Cell list

Cell list is shown in Table 11. They have the same function and pin interface.

Table 11 Cell list

| # | Cell name | Description |
| --- | --- | --- |
| **1** | dwc_ucie2phy_dca | Support both UCIe-A/S, NS/EW PHY orientation |

## Features

Maximum clock frequency: 10GHz

Duty cycle adjustable range: +/-10% at max frequency and typical condition

## Recommended Operating Conditions

Table 12 : Recommended operating conditions

| Parameter | Description | Min | Typ | Max | Unit |
| --- | --- | --- | --- | --- | --- |
| VDD | Core supply Voltage (normal mode) | 0.675 | 0.75 | 0.825 | V |
| VSS | Core ground Voltage | 0 | 0 | 0 | V |
| Tj | Junction Temperature | -40 | 25 | 125 | 0C |

# Architecture

## Functional Block Diagram

A Functional and Digital Control block diagrams of the DCA are shown in the two figures below:

Figure 21 DCA block diagram

## Core DCA

In DCA, there is an analog block that contains 2 DCA stages connected in series. Each step consists a coarse cell and a fine cell. These coarse and fine cells serve to adjust the duty cycle of the input clk and generate this adjusted clk signal at the output.

Figure 22 Core DCA block diagram

## Coarse Cell

Each DCA stage has totally 5 input coarse tuning bits PclkDcaCoarse[4:0] fed to the coarse decoder to generate 4 control bits for the pull-down networks of the coarse sub-block ncoarse[3:0] and 4 control bits for the pull up networks of the coarse sub-block pcoarse[3:0].

The decoder logic table are shown as below table:

Table 21 - Coarse decoder logic table

| PclkDcamode | PclkDcaCoarse[4:0] | **Bin** | pcoarsectl[3:0] | ncoarsectl[3:0] | Note |
| --- | --- | --- | --- | --- | --- |
| 1 | 10100 | **0** | 1100 | 1100 |  |
| 1 | 10011 | **1** | 1000 | 1100 |  |
| 1 | 10010 | **2** | 1000 | 1101 |  |
| 1 | 10001 | **3** | 1000 | 1111 |  |
| 1 | **00000** | **4** | **0000** | **1111** |  |
| 1 | 00001 | **5** | 0010 | 1111 |  |
| 1 | 00010 | **6** | 0010 | 0111 |  |
| 1 | 00011 | **7** | 0010 | 0011 |  |
| 1 | 00100 | **8** | 0011 | 0011 |  |
| 0 | xxxxx | **x** | 11110000 | 00001111 | In default mode, DCA is forced to middle code |

**Note:**

- The Bin column is only recommended for RTL implement. It is independent with DCA circuit design.
- PclkDcaCoarse[4:0] : binary coded and ranges from (0 to 8) where code (4) corresponds to higher resolution and lower span.
- A schematic view of the coarse buffer are shown as the below figure:
Figure 23 A coarse inverter schematic

## Fine Cell

DCA has totally 4 inputs fine tuning PclkDcaFine[3:0] bits fed to the digital control block (internal decoder within the analog domain) to generate 6 control bits for the pull down networks of the Fine sub-block nfinectl[5:0] and 6 control bits for the pull up networks of the Fine sub-block pfinectl[5:0].

The combination of all these control signals results in 13 fine codeword settings of the DCAas shown in Table 9 below.

Duty cycle of the input clock can be reduced or increased in the range defined in electrical parameters.

Code 6 represents zero duty cycle adjustment at which the fine sub-block operates at its minimum strength and codes 0 and 12 represent the minimum and maximum duty cycle output respectively. A schematic view of the fine sub-block is shown in Figure 4 below.

Table 22- Fine decoder logic table

| **PclkDcaMode** | **PclkDcaFine ****[****3:0****]** | **Bin** | **pfinectl****[****5:0****]** | **nfinectl****[****5:0****]** | **Notes** |
| --- | --- | --- | --- | --- | --- |
| 1 | 1110 | 0 | 111000 | 111000 | min duty cycle output (50-X)% duty cycle output |
|  | 1101 | 1 | 111100 | 111000 |  |
|  | 1100 | 2 | 111100 | 011000 |  |
|  | 1011 | 3 | 111100 | 001000 |  |
|  | 1010 | 4 | 111110 | 001000 |  |
|  | 1001 | 5 | 111111 | 001000 |  |
|  | **0000** | **6** | **111111** | **000000** | 50% duty cycle output |
|  | 0001 | 7 | 111111 | 000001 |  |
|  | 0010 | 8 | 110111 | 000001 |  |
|  | 0011 | 9 | 100111 | 000001 |  |
|  | 0100 | 10 | 100111 | 000011 |  |
|  | 0101 | 11 | 100111 | 000111 |  |
|  | 0110 | 12 | 000111 | 000111 | max duty cycle output (50+X) % duty cycle output |
| 0 | xxxx | x | 011011111111 | 100100000000 | In default mode, DCA is forced to middle code |

Figure 24 Fine Cell

## DCA Calibration

DCA gets optimal code by sweeping coarse and fine value until dcd getting closest to 50%. The detail of DCA training process is described in Functional section.

Figure 25 DCD(%) vs DCA coarse

# Pin list

Table 31 Pin list

| **Pin name** | **Direction** | **Signal Width** | **Power Domain** | **Clock domain** | **Function** |
| --- | --- | --- | --- | --- | --- |
| VDD | Input | 1 | VDD | Async | Digital Logic Power Supply |
| VSS | Input | 1 | 0 | Async | Ground |
| PclkIn | Input | 1 | VDD | Pclk | Input Pclk from Master/Repeater |
| PclkOut | output | 1 | VDD | Pclk | PCLK Out to first DCA |
| DCACoarse | Input | 5 | VDD | Async | Coarse Control Digital Word for Coarse Duty-Cycle Adjust, Default 0 for 50% input Duty Cycle |
| DCAFine | Input | 4 | VDD | Async | Fine Control Digital Word for Coarse Duty-Cycle Adjust, Default 0 for 50%input Duty Cycle |
| PclkDcaMode | Input | 1 | VDD | Async | DCA enable signal/ When PclkEn is HI and PclkDCAMode is HI, DCA is enable |

# Functional Description

## Operation modes

The DCA operates in two different modes:

Mission mode: PclkIn passes through DCA with the ***calibrated****** ******code******.***

Default mode: PclkIn passes through DCA with ***default ******code******.***

Table 41 - Operation modes

| DcaMode | Comment |
| --- | --- |
| 1 | Mission mode |
| 0 | Default mode |

## DCA Calibration

### Optimal code of DCA

***The optimal code of DCA is the code whe******re****** DCD output is*** ***toggling****** ******between 0 and 1****** ******in one****** fine step****.*

As the DCA code changes, it effects to the duty cycle at the DCD (duty cycle detector) where the clock duty cycle is sensed.

The output of DCD (duty cycle detector) behaves as below:

dcd_out = 0: duty cycle at DCD [ 50%

dcd_out = 1: duty cycle at DCD ] 50%

### Calibration Process.

Refer to the *UCIe** PHY Functional and Architecture Specification* section 5.4.4.3 DCA Calibration

Step 1 – initial phase – checking at central point:

Set the coarse codes in middle value: coarse = 4, fine=6. Checking dcd_out:

If dcd_out does not toggle in above process, the next step depends on dcd_out value:

dcd_out=0, go to Step 2.2

dcd_out=1, go to Step 2.1

Step 2.1 – Pulse width high Reducing calibration:

Sweep the coarse from 4 to 0. For each coarse value, do lower fine sweep to find fine code.

Step 2.2 – Pulse width high Extending calibration:

Sweep the coarse from 4 to 8. For each coarse value, do upper fine sweep to find fine code.

Figure 41: DCA behavior graph

Figure 42 DCA Calibration Sequence

Note: All the numbers of DCACoarse/DCAFine is based on the **BIN**** **column in Table 21/Table 22.

## DFT Mode

In DFT mode, set PclkDcaMode to 0.

## IDDQ Measurement

In IDDQ mode, set PclkDcaMode to 0.

## Burn-in Mode

In Burn-in mode, set PclkDcaMode to 0.

# RTL and timing constraints

## RTL constraints

Table 51 RTL constraints

| Parameter | Value | Macro | Description |
| --- | --- | --- | --- |
| **tDCA_update_to_DCD** | 150ns | dca | Time requires from DCA update new code PclkDcaCoarse[4:0] and PclkDcaFine[3:0] until dcd_out of DCD valid for captured data. It’s included DCDSettleTime from DCD |
| **tDCA_update_to_PclkOut** | 1ns | dca | Time requires from DCA update new code PclkDcaCoarse[4:0] and PclkDcaFine[3:0] until output pin PclkOut of DCA valid. |
| **tPclkDcaMode_update_to_PclkOut** | 1ns | dca | Time requires from DCA change from mission mode to default mode via versa until output pin PclkOut of DCA valid. |

## Delay parameters

Table 52 Delay parameter

| Parameters | Min | Typ | Max | Unit | Description |
| --- | --- | --- | --- | --- | --- |
| **dca_zero_range** | 45 |  | 150 | ps | Insertion Delay |
| **dca_zero_skew_dword** |  |  | 4 | ps | Delay skew among DCA within DWORD |
| **dca_coarse_step** |  |  | 7 | ps | Step of coarse delay @8GHz |
| **dca_fine_step** |  |  | 1 | ps | Step of fine delay @8GHz |
| **dca_adj_range** | 12.5 |  |  | ps | DCA adjustable range over frequencies |

# Simulation Plan

Table 61 Verification testbench

| **No.** | **Test-bench** | **Simulation type** | **bbSim** | **Description** |
| --- | --- | --- | --- | --- |
| 1 | dca_mission_timing | normal | yes | Transient sim of DCA (Mission mode) at coarse =4, fine =6Measure timing (delay, DCD, slew) and current consumption |
| 2 | dca_mission_timing_monte | monte | yes | Monte Carlo sim of dca_mission_timing_pre/post |
| 3 | dca_mission_timing_aging_she | aging | yes | Aging sim of dca_mission_timing_pre/post |
| 4 | dca_default_timing | normal | yes | Transient sim of DCA (Default mode)Measure timing (delay, DCD, slew) and current consumption |
| 5 | dca_default_timing_monte | monte | yes | Monte Carlo sim of dca_default_timing_pre/post |
| 6 | dca_default_timing_aging_she | aging | yes | Aging sim of dca_default_timing_pre/post |
| 7 | dca_stepsize | normal | yes | Measure step DCD, dcd range, INL, DNL |
| 8 | dca_stepsize_monte | monte | yes | Monte Carlo sim of dca_stepsize_pre/post |
| 9 | dca_dcd_train | normal | yes | Measure optimal code of DCA by observing dcd_out of DCD |
| 10 | dca_dcd_offsetcal_monte | monte | yes | Measure offset code of DCD at each sample of Monte Carlo |
| 11 | dca_dcd_train_monte | monte | yes | Monte Carlo sim of dca_dcd_short_train_pre/post |
| 12 | dca_mission_min_pw | normal | yes | Measure minimum input pulse width that DCA can cover |
| 13 | dca_mission_min_pw_monte | monte | yes | Monte Carlo sim of dca_mission_min_pw_pre/post |
| 14 | dca_power_LP2 | normal | yes | Measure leakage current when input signal off @mission mode and @default mode |
| 15 | dca_power_LP3 | normal | yes | Measure leakage current when input signal off @mission mode and @default mode |
| 16 | dca_cck_pre | cck | yes | Dynamic CCK |
| 17 | dca_emir_she | emir | yes | EMIR sim of DCA (Mission mode) at coarse = 4, fine = 6 |
| 18 | dca_mission | cosim | yes | Functional verification @mission mode |
| 19 | dca_default | cosim | yes | Functional verification @default mode |
