**UCIe gen2 Receiver IO specification**

Databook

Library: dwc_ucie2phy_rx

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

# Revision History

| **Date** | **Owner** | **Revision** | **Description** |
| --- | --- | --- | --- |
| Jan 30, 2026 | Tri Vo | 2.65 | Update RXSIM architecture to address timing issue at low data rate () |
| Dec 04, 2025 | Tri Vo | 2.6 | Update truth table of RX and RXCKTRK Async mode: RxOccEn = 0 X Loopback mode: RxOffsetEn = 1 0 DFT mode: remove requirement RxAsyncEn = 0 (Customer requests to run both scan and flyover at the same time) |
| Oct 24, 2025 | Tri Vo | 2.5 | Rename rxsim16b to rx16b Rename rxcalsim to rxcal Analog CTLE training: add more 3 ACgain configs () |
| Sep 30, 2025 | Tri Vo | 2.4 | Update RXCAL to support new FIFO calibration (). RXSIM: add pin RxSimSe to support DFT scan test |
| Sep 22, 2025 | Tri Vo | 2.3 | Update truth table of RX* sub-blocks (change from operation mode based to interface pin based) |
| Aug 29, 2025 | Tri Vo | 2.26 | rxcal16bsim: Change RxSimDat to RxSimDat[3:0] Increase number of SIM phase detector RX: Update section “4.7.10 Optimal analog configuration training” with skip option () Update operation waveform of RX mission mode |
| Aug 21, 2025 | Tri Vo | 2.25 | Update block diagram and waveform of PRBS loopback |
| Aug 12, 2025 | Quyen Le Tri Vo | 2.2 | RX: Update Sampler offset compensation sequence Update description and truth table of Analog sub-blocks (), including voltage attenuator. Update new PRBS7 for loopback () Remove RxClkOut, RxLbDin[7:0], RxLbDout[7:0], RxLbSo. Change RxSi[1:0] to RxSi, RxSe[1:0] to RxSe Add new pin RxPrbsEn |
| Jul 19, 2025 | Tri Vo | 2.15 | rx16bsim: RxSimMode synchronizer from 2 flops to 6 flops () |
| Jul 08, 2025 | Tri Vo | 2.1 | Add new macro rxcal16bsim to support SIM clock calibration |
| Jun 25, 2025 | Tri Vo | 2.0 | RX SIM: Update logic to support scan RXCKTRK: update truth table () Add 2 new lines for Untrained link – calibration phase |
| Jun 14, 2025 | Tri Vo | 1.95 | Add RX SIM |
| Jun 05, 2025 | Quyen Le | 1.9 | RX Update Sampler offset compensation sequence Update t_settling_time_offset_code = 20ns for all step codes |
| May 12, 2025 | Tri Vo | 1.85 | RX Update RX FIFO Add pin RxRdPtr[1:0] Remove VPH Change ESD and VDAC to VCCIO domain since PHY VCCIO is always support high level RXCKTRK Remove VPH Add pin RxAttRpu[1:0] and RxAttRpd[1:0] Change ESD and VDAC to VCCIO domain since PHY VCCIO is always support high level RXCAL: Change RdPtr to RxRdPtr and direction from output to input Support DFT Scan |
| May 08, 2025 | Tri Vo | 1.8 | Remove cell rx8b*, rxcal8b* Change RX PIPE to RX FIFO Rename pin RxNegCEn to RxVcmAdj Change RxResetn to RxResetn[1:0] Update Loopback: Roll back to 8-bit loopback data in/out Add AND gate before Clock div2 Update section 4.6.10: AC configuration sweep Update RXCAL: add fifo point calibration circuit |
| Apr 15, 2025 | Nguyen Nguyen Tri Vo | 1.7 | Update truth table for all mode RX and RXCKTRK (Section 4.7) Update timing constraint for Offset pins (Section 4.10.1) Clarify RXCKTRK does not need training optimal analog config (4.8.10) Update RX_VGA output tie_high when disabled (Section 4.8.1.2) Update RXCKTRK_CML2CMOS having 1 output only (Section 4.8.2.3) Fix typo for DFT Scan chain for RX loopback (Section 4.7.7.1.2) |
| Apr 11, 2025 | Nguyen Nguyen Tri Vo | 1.6 | Update timing constraint for Offset pins (Section 4.10.1) Change cell name following the new conventional name (UCIe-A/S and PHY orientation). Rename rxdc_term to rxodt |
| Jan 20, 2025 | Nguyen | 1.5 | Increase RxOffsetSel_* bus width from 6 to 7 Update value of RxData[0:7] when RxEn=0 (Section 4.5.1.1) Set 25ps as delay from RxClk_270 to RdClk for BEH model (4.5.1.1) Update value of RxClk[0:1] when RxEn=1, RxIn_VIO hiZ (Section 4.5.1.2) Set CDR section (4.6.12) to Not Supported |
| Jan 13, 2025 | Tri Vo | 1.4 | Increase RxOffsetSel_* bus width from 5 to 6 Add pin RxUcieLikeEn Add section for Idle and standby configuration |
| Dec 23, 2024 | Nguyen Nguyen | 1.34 | RX: Update ESD & VDAC using VDD RXCKTRK: Update ESD & VDAC using VDD Update constraint for VCCIO: VCCIO ≤ VDD+100mV (section 3.1.1) Add constraint input maximum swing: ≤ VDD+100mV (section 3.1.2 and 3.1.3) Update Optimal analog configuration training (section 4.6.10) |
| Dec 11, 2024 | Tri Vo | 1.32 | RX: Remove RxSo[0]. Scan chain output is RxData[7] Change RxSo[1] to RxLbSo RXCKTRK: Remove RxSo. Scan chain output is RxTrkClk[3] |
| Dec 07, 2024 | Nguyen Nguyen | 1.3 | RXCKTRK: Update block diagram to map with schematic: Using 1 S2D after MUX Update clock gater with pause signal Update pin description for vbiasp related to RxVbias in 4.6.1 and 4.6.2 section New macro: dwc_ucie2phy_rx_cal () |
| Nov 19, 2024 | Tri Vo | 1.2 | RX: update scan chain from 3 to 2 () RXCKTRK: Add pin RxClkGtAsynEn to support strobe mode in MBINIT Add note in Table 415 |
| Nov 07, 2024 | Nguyen Nguyen | 1.1 | RX Update pin description: Tie low for dummy pin RXCKTRK Add pin RxClkGtEn () Add pin RxClkOutEn () |
| Nov 04, 2024 | Nguyen Nguyen | 1.06 | RXCKTRK Update block diagram: clarify logic control for gating RxClkOut, RxClkIn_* and RxTrkClkIn |
| Oct 30, 2024 | Nguyen Nguyen | 1.05 | RXCKTRK Update block diagram: use RxOccEn to enable RxTrkClkIn directly to RxClk[1:0] to support for DFT mode Update pin description: RxClkIn_*, RxTrkClkIn, RxClkOut Update truth table RXCKTRK_CML2CMOS (4.6.2.3) Update truth table RXCKTRK_VGA (4.6.2.2) Update DFT requirement Update block and timing diagram for loopback (4.5.2) |
| Oct 25, 2024 | Nguyen Nguyen | 1.01 | RX Update pin description: clarify which is dummy pins RXCKTRK Update pin description: clarify which is dummy pins and clarify some status of pins follow input control Update block diagram and truth table for RX_ANA and RXCKTRK_ANA (4.6.1 and 4.6.2) |
| Oct 06, 2024 | Tri VoNguyen Nguyen | 1.0 | RX Phase Deskew bus width from 4 to 5 to support RX lane-lane deskew Add section for RX lane-lane deskew algorithm (4.7.7) Update Loopback mode (P80001562-533260) Update Loopback mode section (4.5.2) Remove CDR in block diagram Update truth table for AFE when VDAC = 0 (4.6.1.1) RXCKTRK Change pin RxLbDinSel to pin RxDiffClkSel Phase Deskew bus width from 4 to 5 Update MUX for low data rate mode (P80001562-535290) Update truth table for AFE when VDAC = 0 (4.6.1.1) Remove cell TXLB |
| Sep 20, 2024 | Nguyen NguyenTri Vo | 0.95 | RX: Update block diagram: clarify operation of sampler and loopback mode Add pin RxReserved[5:0] RXCKTRK Update block diagram: modify block diagram to match with schematic Update Loopback mode (4.6.2) Update CML2CMOS to differential output (4.7.2.3) Update Clock duty cycle and I/Q calibration (4.7.9) New cell 4.5dwc_ucie2phy_txlb to support localized loopback architecture () |
| Sep 18, 2024 | Nguyen Nguyen | 0.9 | RX: Update block diagram support localized prbs loopback Change pin RxLbDin to RxLbDin[3:0] Add pin RxLbBdl[2:0] Rename RxOffSetCalEn to RxOffsetCalEn in RX_ADV RXCKTRK Update block diagram: change RxLbDin go into RXCK_ANA Change Strong Arm Latch to active low and update mux distribute clock to SA Latch to inverted mux Add initial version for TXLB (4.5) Add training sequence for Optimal analog config training (4.7.8) |
| Sep 13, 2024 | Nguyen Nguyen | 0.81 | Update RX block diagram: Move DIV2 to before BDL |
| Sep 09, 2024 | Nguyen Nguyen Tri Vo | 0.8 | Update RX Operation modes (4.5.1) Update RTL timing constraint (4.8.1, 4.8.2) Rename RxOffSetCalEn to RxOffsetCalEn Add cell rx_std and rxcktrk_std |
| Aug 29, 2024 | Nguyen Nguyen | 0.71 | RX (Production version) Update block diagram: move DIV2 block into RX PIPE RXCKTRK (Production version) Reduce RxTrkClk[7:0] from bus 8 to bus 4 Update block diagram Update DFT section for RXCKTRK (4.5.4.2.2) Update block diagram for RX PIPE (4.6.5) Remove the section of Aug TC |
| Aug 20, 2024 | Nguyen Nguyen | 0.7 | RX (Production version) Rename RxPowerMode[1:0] to RxCurrAdj[1:0] Rename RxVbias_p to RxVbias Increase RxSe[1:0], RxSi[1:0], RxSo[1:0] from bus 2 to bus 3 Reduce RxResetn[1:0] from bus 2 to single pin RxResetn Increase RxData[3:0] from bus 4 to bus 8 Add pin RxOffSetCalEn, RxClkOut, RxOccEn Remove pin related to FIFO: RxWrPtrInit, RxRdPtrInit, RxWrPtr[1:0], RxRdPtr[1:0] Remove pin RxOccEn, RxSeCg, RxPhyClk Replace RX FIFO block by RX PIPE block RXCKTRK (Production version) Rename RxVbias_p to RxVbias Rename RxPowerMode[1:0] to RxCurrAdj[1:0] Increase RxTrkClk[1:0] from bus 2 to bus 8 Remove pin RxClkAdj, RxClkEn Add pin RxClkOut, RxSo Add pin RxTrkDatClkSel, RxClkPhSel, RxLbDinSe, RxSi, RxSe, RxOccEn Add pin RxClkIn_90,180,270 Add pin RxClkBdl_90,180,270[3:0] Remove cell RX_CAL Remove cell DFF Update section DFT for RX and RXCKTRK (4.5.4) Update Sampler offset compensation (4.7.6) Replace section RX FIFO by RX PIPE (4.7.5) |
| Aug 07, 2024 | Nguyen Nguyen | 0.65 | RXCKTRK (Production version) Rename RxClk_0 to RxClkIn_0 Rename RxTrkClk to RxTrkClkIn Rename RxTrkCk[1:0] to RxTrkClk[1:0] |
| Aug 02, 2024 | Nguyen Nguyen | 0.64 | RXCKTRK (Production version) Rename cell from RXCK to RXCKTRK Add pin RxClk_0, RxClkBdl_0[3:0], RxTrkClk, RxTrkData[1:0], RxTrkClk[1:0] Remove pin RxData Update block diagram support for TRK function RX_CAL Update block diagram: adding NOT to AND (jira ) Update Sampler offset cancellation (Section 4.7.7) |
| Jul 01, 2024 | Nguyen Nguyen | 0.63 | RXCK (Production version) Add pin RxResetn into RXCK RX_CAL (Production version) Update rxfifo connection: only care data [3] () Add pin for CKN phase adjustment: RxClkAdjInit, RxClkAdjEn, RxClkAdjInit () |
| Jun 26, 2024 | NguyenNguyen | 0.62 | Update block diagram for RX Aug TC using StrongArm Update truth table for Mission mode of RXCK Update block diagram and pin description for RXDQ ANA Update block diagram and pin description for RXCK ANA Update max frequency of Async mode to 400Mhz Update block functionality for RXCMOS |
| Jun 21, 2024 | Nguyen Nguyen | 0.61 | Update block diagram and pin description for RX Production Rename pin RxCountUp, RxCountDown by RxEarly, RxLate Rename pin RxDfeEn to RxSamplerEn Add pin RxOccEn Update block diagram and pin description for RXCK Production Remove pin RxOccEn, RxOccIn Update block diagram for FIFO Add pin OccEn Update section 4.7.4 Sampler offset cancellation Add CDR description |
| Jun 11, 2024 | NguyenNguyen | 0.6 | Update block diagram and pin description for RX Production Add domain power VPH Add 16 pins control for BDL: RxClkBdl_*[3:0] Add 3 pin for CDR: RxCdrEn, RxCountUp, RxCountDown) Add pin offset enable and 20 pin offset select Remove pin RxGen1En, RxMatchSel* Remove pin RxDfeSel[1:0] Update block diagram for RXCK TC Aug Remove Matchcell in block diagram Update block diagram and pin description for RXCK Production Add domain power VPH, VDDREG Add 2 pins for flyover mode: RxAsyncEn, RxDatAsync Add 2 pins for OCC clock: RxOccIn, RxOccEn Add 3 pins for differential clock mode: RxClkMode, RxClkEn, RxClkAdj Update to differential clock output RxClk[1:0] Update block diagram/pin of rxcal New pin RxClkBdl_*[3:0] Add section for RXCK clock calibration (Section 4.7.1) Add IDDQ and burn-in test recommendation |
| May 29, 2024 | Nguyen Nguyen | 0.51 | Correct operation of VDAC (Section 4.7.4) |
| May 27, 2024 | Nguyen Nguyen | 0.5 | Adding block diagram TC Aug for RX (Section 4.1.1) |
| May 24, 2024 | Nguyen Nguyen | 0.4 | Adding section 4.6.3 Flyover Mode |
| May 03, 2024 | Nguyen Nguyen | 0.3 | Update pin description and block diagram for rx and rx_std Add RxSeCg Add RxPwrOk_VAON, VCCAON Fix spell *PtrInt -> *PtrInit Update bit width for pin RxSi, RxSo, RxWrPtr Update latest Fifo Update pin description and block diagram for rxcktrk and rxcktrk_std Remove RxBiasEn, RxCurrAdj[3:0] Add RxPwrOk_VAON, VCCAON Change RxVbias_p from output to input dwc_ucie2phy_rx_cal: o Add pins for Scan mode RxSe[1:0] RxSeCg RxSi[1:0] RxSo[1:0] o Change pin CalOut[3:0] to CalOut |
| Apr 22, 2024 | Tri Vo | 0.2 | Add cell dwc_ucie2phy_rx_cal |
| Mar 28, 2024 | Nguyen Nguyen | 0.13 | Update pin of FIFO and RXDQ using quadrature rate clock Update RXCK with TRK function and remove DFE control pin |
| Mar 12, 2024 | Nguyen Nguyen | 0.12 | Add Fifo and remove Clock divider and De-serializer form RXDQ Add DFT information |
| Jan 22, 2024 | Tri Vo | 0.11 | Change cell name prefix uciephy to ucie2phy |
| Sep 20, 2023 | Duc Duong | 0.1 | Initial version |

# Introduction

The UCIe 2.0 interface I/O Buffers are high speed I/O buffers designed for die-to-die interface over short communication channels.

These buffers are designed to meet the requirements of different communication channels over an interposer to drive and receive data between dies that are in close proximity to the control device.

- High Bandwidth DQ, DQS and CMOS receivers
- Target speed 40Gbps, 20GHz
- Temperature range -40C to 125C
# Overview

## *Input** **Specification*

### Common Input Specification

| Parameters | Specification | Note |
| --- | --- | --- |
| UCI Standard | 2.0 |  |
| Max Speed | Mainband, RX*, RXCKTRK*: 40Gbps/20Ghz Sideband, RXSB: 1Gbps/1GHz Async mode: 400MHz |  |
| Design features | Vref DAC training per bit CTLE equalizer to compensate for channel loss Bias generator per DW Internal core loopback |  |
| VDD | 0.75V+/-10% |  |
| VCCIO | UCIe -S: 0.5V+/-10%, 0.75V+/-10% , 0.7V+/-10% UCie-A: 0.5V+/-10% | VCCIO require constraint: VCCIO ≤ VDD+100mV |
| VCCAON | 0.75V+/-10% |  |
| RX clock | Quadrature |  |
| ESD Spec | 0.15A: UCIe-A 0.30A: UCIe-S |  |

### *RX***** (UCIe-A) and RX*****_STD (UCIe-S)** Input Specificatio**n*

| Parameters | Spec | Note |
| --- | --- | --- |
| Input small eye height | +/-20mV |  |
| Input maximum swing | ≤VDD + 100mV |  |
| Input Eye width | 0.4UI |  |
| Input common mode | UCIe-A: VCCIO/2 UCIe-S: Terminated: + 0.5V VCCIO: min 90mV – max 130mV + 0.75V VCCIO: 150mV – max 220mV Unterminated: VCCIO/2 |  |
| Input Slew rate | 4.5V/ns |  |
| PAD CAP | UCIe-A: 200fF UCIe-S: 200fF |  |
| RX Termination Impedance | UCIe-S: 50 Ohm +/-5 Ohm |  |
| RX Impedance step size | 1 Ohm |  |

### RXCKTRK (UCIe-A) and RXCKTRK_STD (UCIe-S) Input Specification

| Parameters | Spec | Note |
| --- | --- | --- |
| Input small eye height | +/-20mV |  |
| Input maximum swing | ≤VDD + 100mV |  |
| Input Eye width | 0.4UI |  |
| Input common mode | UCIe-A: VCCIO/2 UCIe-S: Terminated: + 0.5V VCCIO: min 90mV – max 130mV + 0.75V VCCIO: 150mV – max 220mV Unterminated: VCCIO/2 |  |
| Input Slew rate | 4.5V/ns |  |
| PAD CAP | UCIe-A: 200fF UCIe-S: 200fF |  |
| RX Termination Impedance | UCIe-S: 50 Ohm +/-5 Ohm |  |
| RX Impedance step size | 1 Ohm |  |

### RXSB Input Specification

| Parameters | Spec | Note |
| --- | --- | --- |
| Input Voltage high (VIH) | Min: 0.7*VCCAON |  |
| Input Voltage low (VIL) | Max: 0.3*VCCAON |  |

## Performance Specification

### *RX (UCIe-A) and RX_STD (UCIe-S)*

| Parameters | Spec | Notes |
| --- | --- | --- |
| Data dependent jitter | **18****.****1****25 ****ps** |  |
| Offset range | **UCIe-A****:**** **-90mV to 100mV **UCIE-S****:**** **-55mV to 65mV |  |
| Power | **UCIe-A****:**** ** **+ ** **UCIE-S****:** **+ ** | **Need TOPSIM provide** |
| DAC Output Voltage | 0.2% VCCIO – 99.8%VCCIO |  |
| DAC resolution (DNL) | 0.2% VCCIO |  |
| **Power supply induced jitter (psij)** | UCIE-A: 0.6 ps/mV UCIE-S: 0.6 ps/mV |  |

### RXCKTRK (UCIe-A) and RXCKTRK_STD (UCIe-S)

| **Parameters** | **Spec** | **Notes** |
| --- | --- | --- |
| **Duty cycle distortion ** | **-****1****% to ****1****% ** | **Post**** ****calibration** |
| **First edge pulse widt****h skew (high/low)** | **10p****s** |  |
| **Offset ** | **UCIe-A****: **-90mV to 100mV **UCIE-S****: **-55mV to 65mV |  |
| **Power** | **UCIe-A** **UCIE-S** |  |
| **Standby recovery (IE)**** time** | **20n****s** |  |
| **Power down recovery (bias)** | **400n****s** |  |
| **VREF DAC settling ****t****ime** | **50ns** |  |
| **DAC Output Voltage** | 0.2% VCCIO – 99.8%VCCIO |  |
| **DAC resolution (DNL)** | 0.2% VCCIO |  |
| **Max capacitance at ****Rx clock** | 40fF |  |
| **Power supply induced jitter (psij)** | 0.2 ps/mV |  |

### RXSB

| **Parameters** | **Spec** | **Notes** |
| --- | --- | --- |
| **Duty cycle distortion (sbclk)** | **3%** |  |
| **Max capacitance at RxOut** | **20fF** |  |
| **Power average** | **30uA** | **At Typical** |

# Mainband Receivers

## dwc_ucie2phy_rx16b_a_*

### Overview

dwc_ucie2phy_rx16b_a_* is high speed data receiver for Advance package design (UCIe-A) with 8 bits output data. The cell list is shown in Table 41. They have the same function and pin interface.

Table 41 List of instances of rx16b_a

| # | Cell name | Description |
| --- | --- | --- |
| **1** | dwc_ucie2phy_rx16b_a_ns | Support UCIe-A, NS PHY orientation |
| **2** | dwc_ucie2phy_rx16b_a_ew | Support UCIe-A, EW PHY orientation |

### Block diagram

Figure 41 Block diagram of dwc_ucie2phy_rx16b_a_ns/ew

The macro contains the following.

- ESD protection
- High speed analog front-end (RXDQ_AFE)
- StrongArm latch to sampler data from 1 to 4
- Offset calibration for 4 StrongArm latches
- RX PIPE with 8 outputs
- Scan chain for flipflop chain in RX PIPE
- RXCMOS to receive asynchronous data input
- Loopback mode
- Internal 8 bits DAC
- 4 Phase Deskew to deskew 4 phases of clock
The entire macro is built with thin gate device, powered under VDD. The Vref input for the amplifier is generated by the internal VDAC block. The analog front-end amplifier is enabled by RxEn. When RxEn = 0, it disables the analog front-end amplifier.

Data input is sampled by Sampler and de-serialize from 1 to 4. Then, data go to Rx Pipe and is read by RxClkDiv2_270.

### Pin description

Table 42 Pin list of mainband data receiver

| **Pin Names** | **Direction** | **Type** | **Power Domain** | **Clock Domain** | **Description** |
| --- | --- | --- | --- | --- | --- |
| VDD | Input | Power | VDD | - | PHY core power |
| VCCAON | Input | Power | VCCAON | - | PHY VCCAON power |
| VCCIO | Input | Power | VCCIO | - | PHY VCCIO power |
| VSS | Input | Ground | VSS | - | Shared ground |
| RxIn_VIO | Input | Digital | VCCIO | RxClk* | Input PAD |
| PhyClk | Input | Clock | VDD | PhyClk | FIFO read clock |
| RxRdPtr[1:0] | Input | Digital | VDD | PhyClk | FIFO read pointer |
| RxClk_0 | Input | Clock | VDD | RxClk_0 | Clock for sampler phase 0 |
| RxClk_90 | Input | Clock | VDD | RxClk_90 | Clock for sampler phase 90 |
| RxClk_180 | Input | Clock | VDD | RxClk_180 | Clock for sampler phase 180 |
| RxClk_270 | Input | Clock | VDD | RxClk_270 | Clock for sampler phase 270 |
| RxClkBdl_0[4:0] | Input | Digital | VDD | RxClk_0 | Fine tune for RxClk_0 |
| RxClkBdl_90[4:0] | Input | Digital | VDD | RxClk_90 | Fine tune for RxClk_90 |
| RxClkBdl_180[4:0] | Input | Digital | VDD | RxClk_180 | Fine tune for RxClk_180 |
| RxClkBdl_270[4:0] | Input | Digital | VDD | RxClk_270 | Fine tune for RxClk_270 |
| RxCdrEn | Input | Digital | VDD | Async | Enable for CDR block (Dummy Pin - user must tie low by using pin soff_VSS to avoid an additional tielow cell in higher level) |
| RxCurrAdj[1:0] | Input | Digital | VDD | Async | 00: Lower data rate 01: For 24Gbps data rate 10: For 32Gbps/40Gbps data rate (default) 11: Higher power for back up |
| RxEn | Input | Digital | VDD | Async | Receiver enable signal. 0: Disable receiver 1: Enable receiver |
| RxResetn[1:0] | Input | Digital | VDD | Async | Reset FF in RX RxResetn[0]: RxClk domain RxResetn[1]: PhyClk domain |
| RxAsyncEn | Input | Digital | VDD | Async | RX async mode enable, active 1 |
| RxLbEn | Input | Digital | VDD | Async | Loopback mode enable 0: turn off core loopback 1: turn on core loopback |
| RxPrbsEn | Input | Digital | VDD | Async | RX PRBS7 pattern generator enable |
| RxLbBdl[2:0] | Input | Digital | VDD | Async | BDL deskew for loopback data path |
| RxVbias | Input | Analog | VDD | Async | Bias signal |
| RxDacSel[7:0] | Input | Digital | VDD | Async | DAC code input. For more detail, see table 3-10 |
| RxDCgain[1:0] | Input | Digital | VDD | Async | DC gain control. Default value: 11 |
| RxCtleEn | Input | Digital | VDD | Async | CTLE enable, active 1 |
| RxACgain[1:0] | Input | Digital | VDD | Async | AC gain control Default value: 10 |
| RxVcmAdj | Input | Digital | VDD | Async | Adjust CTLE output common mode voltage |
| RxSamplerEn | Input | Digital | VDD | Async | Sampler enable (Dummy Pin - user must tie low by using pin soff_VSS to avoid an additional tielow cell in higher level) |
| RxOffsetEn | Input | Digital | VDD | Async | Enable offset for 4 samplers |
| RxOffsetCalEn | Input | Digital | VDD | Async | Enable for offset calibration phase |
| RxOffsetSel_0[6:0] | Input | Digital | VDD | Async | Offset calibration select bit for data path 0. First bit is sign bit. |
| RxOffsetSel_90[6:0] | Input | Digital | VDD | Async | Offset calibration select bit for data path 90. First bit is sign bit. |
| RxOffsetSel_180[6:0] | Input | Digital | VDD | Async | Offset calibration select bit for data path 180. First bit is sign bit. |
| RxOffsetSel_270[6:0] | Input | Digital | VDD | Async | Offset calibration select bit for data path 270. First bit is sign bit. |
| RxSi | Input | Digital | VDD | Async | Scan input |
| RxSe | Input | Digital | VDD | Async | Scan enable |
| RxOccEn | Input | Digital | VDD | Async | Select clock for DFT mode When RxOccEn=1, bypass clock divider (the output clock frequency is the same as the input clock) |
| RxPwrOk_VAON | Input | Digital | VCCAON | Async | Power ok signal |
| RxReserved[5:0] | Input | Digital | VDD | Async | Reserved pins (Dummy Pin - user must tie low by using pin soff_VSS to avoid an additional tielow cell in higher level) |
| RxUcieLikeEn | Input | Digital | VDD | Async | UCIe-like enable pin. User need to assert it for UCIe noncompliant product. |
| RxAttRpu[1:0] | Input | Digital | VDD | Async | Control Attenuator pull up resistor |
| RxAttRpd[1:0] | Input | Digital | VDD | Async | Control Attenuator pull down resistor |
| RxData[15:0] | Output | Digital | VDD | PhyClk | Receiver data output RxData[15] is also used for RX FIFO scan chain output |
| RxEarly | Output | Digital | VDD | Async | Output from CDR to calibrate clock (Dummy Pin - user must tie low by using pin soff_VSS to avoid an additional tielow cell in higher level) |
| RxLate | Output | Digital | VDD | Async | Output from CDR to calibrate clock (Dummy Pin - user must tie low by using pin soff_VSS to avoid an additional tielow cell in higher level) |
| RxDatAsync | Output | Digital | VDD | Async | Asynchronous receiver data output |
| soft_VDD | Output | Digital | VDD | Async | Tied high output signal |
| soft_VSS | Output | Digital | VSS | Async | Tied low output signal |
| RxSimClk | Input | Clock | VDD |  | High speed clock. This is used to measure phase |
| RxSimSclk | Input | Clock | VDD |  | Slow speed clock. This clock is used to read out the data collected by the SIM chain. |
| RxSimMode | Input | Digital | VDD | Async | Defines whether the monitor is in measurement or collection mode. 0 = measure, 1 = collect |
| RxSimResetn | Input | Digital | VDD | Async | Reset all the flop in the SIM block. This reset may be asserted before new measurement to clear the status flops. |
| RxSimOffsetSel[6:0] | Input | Digital | VDD | Async | Offset calibration bit for SIM sampler. First bit is sign bit. |
| RxSimDatOut | Output | Digital | VDD | RxSimClk | SIM sampler output for the offset calibration purpose |
| RxSimSe | Input | Digital | VDD | RxSimSclk | DFT Scan enable. |
| RxSimSi | Input | Digital | VDD | RxSimSclk | Serial input. This input is used to daisy chain the SIMu chains. The first SIMu has its SI driven by the SIMc. All other SIMu have the SI driven from the SO of the previous SIMu. This pin is also used in DFT scan test. |
| RxSimSo | Output | Digital | VDD | RxSimSclk | Serial output. This output is used to daisy chain the SIMu chains. The last SIMu drives the SIMc with its SO. All other SIMu have the SO driving the SI of the next SIMu. This pin is also used in DFT scan test. |

## dwc_ucie2phy_rx16b_s_*

### Overview

dwc_ucie2phy_rx16b_s_* is high speed data receiver for Standard package design (UCIe-S). The feature is the same as the receiver of UCIe-A, but with the additional on-die termination resistor.

The on-die termination resistor is 50ohm grounded termination. User can enable or disable this termination depending on data rate and channel length.

The cell list is shown in Table 43. They have the same function and pin interface.

Table 43 List of instances of rx16b_s

| # | Cell name | Description |
| --- | --- | --- |
| **1** | dwc_ucie2phy_rx16b_s_ns | Support UCIe-S, NS PHY orientation |
| **2** | dwc_ucie2phy_rx16b_s_ew | Support UCIe-S, EW PHY orientation |

### Block diagram

Figure 42 Block diagram of dwc_ucie2phy_rx16b_s_ns/ew

### Pin description

The pin list is the same as dwc_ucie2phy_rx16b_a receiver, but with additional pins for termination resistor.

Table 44 Additional pin list of Mainband data receiver for UCIe-S

| **Pin Names** | **Direction** | **Type** | **Power Domain** | **Clock Domain** | **Description** |
| --- | --- | --- | --- | --- | --- |
| RxTermResCode[5:0] | Input | Digital | VDD | Async | Calibration code for the on-die termination |
| RxTermGdEn | Input | Digital | VDD | Async | One-die termination enable |

## dwc_ucie2phy_rxcktrk_a

### Overview

dwc_ucie2phy_rxcktrk_a is a pseudo differential receiver used for the clock/track signal and for Advanced package (UCIe-A). It contains primary ESD protection, a pseudo differential receiver converting the PAD into VDD digital signals. In addition, it includes the control logic for low-speed clock calibration.

Table 45 rxcktrk_a list cell

| # | Cell name | Description |
| --- | --- | --- |
| **1** | dwc_ucie2phy_rxcktrk_a_ns | Support UCIe-A, NS PHY orientation |
| **2** | dwc_ucie2phy_rxcktrk_a_ew | Support UCIe-A, EW PHY orientation |

### Block diagram

Figure 43 Block diagram of rxcktrk_a

The macro contains the following:

- ESD CDM protection
- High-speed receiver
- Low-speed receiver for flyover mode
- Loop back path
- Internal 8-bits DAC
The high-speed receiver is a VDD complimentary amplifier using thin oxide for the input differential pair.

### Pin description

Table 46 Pin list of Mainband clock/track receiver

| **Pin Names** | **Direction** | **Type** | **Power Domain** | **Clock Domain** | **Description** |
| --- | --- | --- | --- | --- | --- |
| VDD | Input | Power | VDD | N/A | PHY core power |
| VCCAON | Input | Power | VCCAON | N/A | PHY VCCAON power |
| VCCIO | Input | Power | VCCIO | N/A | PHY VCCIO power |
| VDDREG | Input | Power | VDDREG | N/A | Clean power supply generated by VREG. Clock output stage uses this power. The rest logic uses core VDD including block for flyover mode. |
| VSS | Input | Ground | VSS | N/A | Shared ground |
| RxIn_VIO | Input | Clock | VCCIO | CLK | Analog strobe input from pad; requires CDM protection |
| RxCurrAdj[1:0] | Input | Digital | VDD | Async | 00: Lower data rate 01: For 24Gbps data rate 10: For 32Gbps/40Gbps data rate (Default) 11: Higher power for back up |
| RxEn | Input | Digital | VDD | Async | Receiver enable signal. 0: Disable receiver 1: Enable receiver |
| RxLbDin | Input | Digital | VDD | Async | Core loopback positive clock |
| RxLbEn | Input | Digital | VDD | Async | 0: turn off core loopback 1: turn on core loopback When enable, user must set RxEn to 0 |
| RxAsyncEn | Input | Digital | VDD | Async | RX async mode enable, active 1 |
| RxDacSel[7:0] | Input | Digital | VDD | Async | DAC code input. For more detail, see table 3-10 |
| RxDCgain[1:0] | Input | Digital | VDD | Async | DC gain control. Default value: 11 |
| RxCtleEn | Input | Digital | VDD | Async | CTLE enable, active 1 |
| RxACgain[1:0] | Input | Digital | VDD | Async | AC gain control Default value: 11 |
| RxVcmAdj | Input | Digital | VDD | Async | Adjust CTLE output common mode voltage |
| RxTrkEn | Input | Digital | VDD | Async | Enable for TRK functionRxTrkEn = 1 => Turn off CML2CMOS block |
| RxTrkDatClkSel | Input | Digital | VDD | Async | Input select between TrkClk or FwdClk |
| RxClkPhSel | Input | Digital | VDD | Async | Input select between clk_0 or clk_180 |
| RxDiffClkSel | Input | Digital | VDD | Async | Input select between RxTrkClkIn or Mission mode clock |
| RxClkIn_0 | Input | Clock | VDD | RxClkIn_0 | Clock for sampler phase 0 RxClkIn_0 is gated when (RxTrkEn=0 && RxDiffClkSel=0) |
| RxClkIn_90 | Input | Clock | VDD | RxClkIn_90 | Clock for sampler phase 90RxClkIn_90 is gated when (RxTrkEn=0 && RxDiffClkSel=0) |
| RxClkIn_180 | Input | Clock | VDD | RxClkIn_180 | Clock for sampler phase 180 RxClkIn_180 is gated when (RxTrkEn=0 && RxDiffClkSel=0) |
| RxClkIn_270 | Input | Clock | VDD | RxClkIn_270 | Clock for sampler phase 270RxClkIn_270 is gated when (RxTrkEn=0 && RxDiffClkSel=0) |
| RxClkBdl_0[4:0] | Input | Digital | VDD | RxClkIn_0 | Fine tune for RxClkIn_0 |
| RxClkBdl_90[4:0] | Input | Digital | VDD | RxClkIn_90 | Fine tune for RxClkIn_90 |
| RxClkBdl_180[4:0] | Input | Digital | VDD | RxClkIn_180 | Fine tune for RxClkIn_180 |
| RxClkBdl_270[4:0] | Input | Digital | VDD | RxClkIn_270 | Fine tune for RxClkIn_270 |
| RxTrkClkIn | Input | Clock | VDD |  | Clock for TRK functionRxTrkClkIn is gated when (RxTrkEn==0 && RxDiffClkSel==0 && RxOccEn == 0) |
| RxClkMode | Input | Digital | VDD | Async | Select clock mode:0: Differential mode1: Quadrature mode |
| RxResetn | Input | Digital | VDD | Async | Reset FF in RXCKTRK |
| RxVbias | Input | Analog | VDD | Async | Bias signal for the DQ receivers |
| RxSi | Input | Digital | VDD | RxTrkClkIn | Scan input |
| RxSe | Input | Digital | VDD | Async | Scan enable |
| RxOccEn | Input | Digital | VDD | Async | Select clock for DFT mode |
| RxPwrOk_VAON | Input | Digital | VCCAON | Async | Power ok signal |
| RxClkGtEn | Input | Digital | VDD | Async | Clock gater enable. It is connected to a synchronizer. |
| RxClkGtAsyncEn | Input | Digital | VDD | Async | Clock gater force enable |
| RxClkGtPause | Input | Digital | VDD | Async | Clock pause signal |
| RxClkOutEn | Input | Digital | VDD | Async | RxClkOut force enable |
| RxUcieLikeEn | Input | Digital | VDD | Async | UCIe-like enable pin. User need to assert it for UCIe noncompliant product. |
| RxAttRpu[1:0] | Input | Digital | VDD | Async | Control Attenuator pull up resistor |
| RxAttRpd[1:0] | Input | Digital | VDD | Async | Control Attenuator pull down resistor |
| RxClk[1:0] | Output | Clock | VDDREG | Async | Differential output clock. RxClk[0]: same phase as RxIn_VIO RxClk[1]: complementary of RxClk[0] |
| RxTrkData[1:0] | Output | Digital | VDD | RxTrkClkIn if RxTrkDatClkSel = 0. Otherwise, RxClkIn_0/RxClkIn_90 | Output of RXCKTRK, to support TRK function for Data |
| RxTrkClk[3:0] | Output | Digital | VDD | RxTrkClkIn | Output of RXCKTRK, to support TRK function for Clk RxTrkClk[3] is also used for scan test |
| RxDatAsync | Output | Digital | VDD | Async | Asynchronous receiver data output |
| RxClkOut | Output | Clock | VDDREG | Async | Single output clock from Cml2cmos, same phase with RxIn_VIO (RxTrkEn = 1 || RxDiffClkSel = 0): RxClkOut = 0(RxTrkEn = 0 && RxDiffClkSel = 1): RxClkOut is active Maximum frequency is 4GHz |
| RxVrefOut | Output | Analog | VDD | Async | DAC voltage output |
| soft_VDD | Output | Digital | VDD | Async | Tied high output signal |
| soft_VSS | Output | Digital | VDD | Async | Tied low output signal |

## dwc_ucie2phy_rxcktrk_s

### Overview

dwc_ucie2phy_rxcktrk_s is a pseudo differential receiver used for the clock/track signal and for Standard package (UCIe-S). The feature is the same as dwc_ucie2phy_rxcktrk_s, but with an additional on-die termination resistor. It is 50ohm grounded termination. User can enable or disable this termination depending on data rate and channel length.

Table 47 rxcktrk_s list cell

| # | Cell name | Description |
| --- | --- | --- |
| **1** | dwc_ucie2phy_rxcktrk_s_ns | Support UCIe-S, NS PHY orientation |
| **2** | dwc_ucie2phy_rxcktrk_s_ew | Support UCIe-S, EW PHY orientation |

### Block diagram

Figure 44 Block diagram of rxcktrk_s

### Pin description

The pin list is the same as UCIe-A clock/track receiver, but with additional pin for termination resistor.

Table 48 Additional pin list of Mainband clock/track receiver

| Pin Names | Direction | Type | Power Domain | Clock Domain | Description |
| --- | --- | --- | --- | --- | --- |
| RxTermResCode[5:0] | Input | Digital | VDD | Async | Calibration code for the on-die termination |
| RxTermGdEn | Input | Digital | VDD | Async | One-die termination enable |

## RX Operation modes

### Truth table

#### RX

Table 49 RX truth table

| RxEn | RxAsyncEn | RxOffsetCalEn | RxOffsetEn | RxLbEn | RxOccEn | RxTerm GdEn | Mode | Note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Refer to DFT section | DFT mode |  |  |  |  |  |  |  |
| 0 | 0 | X | X | X | 0 | 0 | Standby | CTLE off, VGA off, output AFE tied high, RXCMOS off, Offgen off, Loopback off |
| 0 | 1 | X | X | X | X | 0 | Async | CTLE off, VGA off, output AFE tied high, RXCMOS on, Offgen off, Loopback off |
| 1 | 0 | 0 | 1 | 0 | 0 | (*) | Mission | CTLE on, VGA on, RXCMOS off, Offgen on, Loopback off |
| 1 | 0 | 0 | 0 | 1 | 0 | (*) | Loopback | CTLE off, VGA off, output AFE tied high, RXCMOS off, Offgen on, Loopback on |
| 1 | 0 | 1 | 1 | X | 0 | (*) | DC offset cancellation | CTLE off, VGA on with input tie_low, RXCMOS off, Offgen on, Loopback on |

- **Notes:**
- The remaining undefined modes, they are not defined but does not cause any electrical damage (No prohibited cases)
- RxTermGdEn is configurable by CSR. It is dependent on channel length and data rate.
#### RXCKTRK

Table 410 RXCKTRK truth table

| RxOccEn | RxEn | RxAsyncEn | RxLbEn | RxTrkEn | RxDiffClkEn | RxClkOutEn | RxClkMode | RxTrkDataClkSel | RxClkPhSel | RxTerm GdEn | Mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Refer to DFT section | DFT |  |  |  |  |  |  |  |  |  |  |
| 0 | 0 | 0 | X | X | X | X | X | X | X | 0 | Standby |
| X | 0 | 1 | X | X | X | X | X | X | X | 0 | Async/Flyover |
| 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | X | X | (*) | Mission Div2 |
| 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | X | X | (*) | Mission |
| 0 | 1 | 0 | 0 | 1 | 0 | 0 | 1 | 1 | X | (*) | Track by clktree |
| 0 | 1 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | X | (*) | Track by PhyClk |
| 0 | 1 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 0 | (*) | Untrained link – Calibration phase Clock output same phase |
| 0 | 1 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 1 | (*) | Untrained link– Calibration phase Clock output revert phase |
| 0 | 1 | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 0 | (*) | Untrained link – Mission phase Clock output same phase |
| 0 | 1 | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 1 | (*) | Untrained link – Mission phase Clock output revert phase |
| 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | X | X | (*) | Loopback Div2 |
| 0 | 1 | 0 | 1 | 0 | 0 | 0 | 1 | X | X | (*) | Loopback at speed |

- **Notes:**
- The remaining undefined modes, they are not defined but does not cause any electrical damage (No prohibited cases)
- RxTermGdEn is configurable by CSR. It is dependent on channel length and data rate.
#### Attenuator Pull up/down Resistor

| **Package** | **IO type** | **VCCIO (V)** | **RxAttRpu[1:0]** | **RxAttRpd[1:0]** |
| --- | --- | --- | --- | --- |
| UCIe-A | Compliance Compatible | 0.45 | 00 | 01 |
|  |  | 0.75 | 00 | 10 |
| UCIe-S | Compliance | 0.45 | 01 | 00 |
|  |  | 0.75 | 00 | 01 |
| UCIe-S | Compatible | 0.75 | 01 | 00 |

### Mission mode

#### RX

Refer to section RX FIFO to get detail operation waveform.

| **Mission mode** | **RxData[7:0]** |
| --- | --- |
| No | *Unknown value (Random 0 or 1) |
| Yes | Input data is sampled with posedge of 4 phases clock RxClk_0/90/180/270 Output is synchronous with posedge of PhyClk 0: if RxIn_VIO<VREF 1: if RxIn_VIO>VREF |

- * Output of AFE tie_high, random output value due to Sampler cannot detect 2 input with same level
#### RXCKTRK

| **Mission mode** | **RxIn_VIO** | **RxClk****[1]/RxClk[0]** | **Note** |
| --- | --- | --- | --- |
| No | x | 1/0 | rxcktrk OFF |
| Yes | z | Unknown value (Random 0 or 1) | Rxcktrk ON, data from TX side is high impedance |
| Yes | 0 | 1/0 | Bias is ON, rxcktrk is ON |
| Yes | 1 | 0/1 | Bias in ON, rxcktrk is ON |

### Loopback mode

- **RX,**** RX****_****STD**
There is built-in PRBS7 pattern generator which can generate two pattern types. The clock frequency is the same as the mission mode clock. Four data out which provides up to 40Gb bandwidth totally.

- Standard PRBS pattern (x7 + x6 + 1)
- Clock pattern when resetn = 0 or prbsen = 0
There are two serializer blocks to generate two bit streams from PRBS7. Two bit streams has the same data but with opposite polarity.

The output of serializer will go to StrongArm latch, then data is transferred to RxData* as in mission mode. The RxOffsetSel* pins of Loopback mode are trained with same sequence of Mission mode (Section 4.8.7)

Figure 45 Block diagram of loopback

Figure 46 Truth table of RX loopback mode

| **Loopback Mode** | **resetn** | **prbsen** | **ser_out** | **ser_outb** |
| --- | --- | --- | --- | --- |
| Yes | 0 | x | 0 | 1 |
| Yes | 1 | 0 | 1010…. | 0101…. |
| Yes | 1 | 1 | prbs7 | !ser_out |

Operation waveform:

Figure 47 Operation waveform of loopback with prbsen=0

Figure 48 Operation waveform of loopback with prbsen=1

- **RXCKTRK_A, RXCKTRK_S**
Table 411 Truth table of RXCKTRK loopback mode

| **Loopback Mode** | **RxLbDin** | **Rx****Clk[0]/RxClk[1]** |
| --- | --- | --- |
| Yes | 1 | 1/0 |
| Yes | 0 | 0/1 |

### Async/Flyover mode

Flyover mode is designed for IO boundary scan feature and applicable for both rx*, rxcktrk*. In this mode, simple differential receiver (with fixed voltage reference – VREF_Async) is used to receive the input data.

The VREF_Async is fixed at VCCIO/3 so that the receiver can work with both VCCIO 0.45v and 0.75v (or equal to core VDD).

Table 412 Truth table for Flyover mode

| RxAsyncEn | RxTermGdEn | RxIn_VIO | RxDatAsync |
| --- | --- | --- | --- |
| **1** | 0 | < VREF_Async | 0 |
| **1** | 0 | > VREF_Async | RxIn_VIO |
| **0** | 0/1 | x | 0 |

- *RxEn = 0 in Flyover mode
### Idle mode

The receiver requires continuous clock mode, so in the idle mode, the configuration is the same as the mission mode:

- RX data: input clock pin is toggle; input PAD is static 0 or 1
- RX clock: input clock pin is toggle; input PAD is toggled with clock pattern
### Standby mode

In this mode, the clock is gated, PAD is static 0 or 1, the analog part of receiver is turned OFF but bias signal is still ON.

### DFT

#### RX

##### Common setting

- RxEn = 0
- RxOccEn = 1
- RxClkBdl_0[4:0] = 5’b0
- RxClkBdl_90[4:0] = 5’b0
- RxClkBdl_180[4:0] = 5’b0
- RxClkBdl_270[4:0] = 5’b0
- RxTermGdEn = 1’b0
##### Scan chain

Table 413 DFT scan chain information

| **Scan chain No.** | **DFT input Clock** | **DFT input data** | **DFT input enable** | **DFT output** | **Sync clock edge** | **Length** | **Description** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PhyClk | RxSi | RxSe | RxData[15] | rising | 16 | Scan chain in RX FIFO 16-bit version |
| 2 | RxSimSclk | RxSimSi | RxSimSe | RxSimSo | rising | 1 | SIM flop, only applicable for RXSIM |

Figure 49 DFT scan chain implementation inside RX FIFO 16-bit

#### RXCKTRK

##### Common setting

- RxEn = 0
- RxOccEn = 1
- RxLbEn=0
- RxTrkEn = 0
- RxDiffClkSel = 0
- RxTrkDatClkSel = 1
- RxClkPhSel = 0 (to select RxTrkClkIn phase 0 for DFT mode)
- RxClkBdl_0[4:0] = 5’b0
- RxClkBdl_90[4:0] = 5’b0
- RxClkBdl_180[4:0] = 5’b0
- RxClkBdl_270[4:0] = 5’b0
- RxTermGdEn = 1’b0
##### Scan chain

**DFT scan chain information**

| **Scan chain No.** | **DFT input Clock** | **DFT input data** | **DFT input enable** | **DFT output** | **Sync clock edge** | **Length** | **Description** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | RxTrkClkIn | Si | Se | RxTrkClk[3] | rising | 4 | rxcktrk_trkclk_sc *red color* |

Figure 410 DFT scan chain implementation inside RXCKTRK

## Blocks functionality

### RX Analog block (RX_ANA)

This cell represents the analog front end for RX. It included ESD, attenuator and CTLE circuitry. This cell needs to be black boxed in equivalence check. It needs its own hierarchy and must be pin matched with circuit.

#### RX Attenuator

RX attenuator is an analog block which is placed before RX CTLE. The main purpose of this block is to provide capability of channel equalizer and input common mode voltage adjustment.

Rs and Cs value are fixed but Rpu and Rpd value are programmable by RxAttRpu/Rpd respectively.

In RX offset voltage calibration mode, the path from RxIn_VIO to OUT is disconnected. Rpu and Rpd are also disabled. OUT is connected to Vdac.

Figure 411 RX attenuator high level diagram

Table 414 Truth table of RX attenuator

| RxAsyncEn | RxOffsetCalEn | att_en | OUT |
| --- | --- | --- | --- |
| 0 | 0 | 1 | RxIn_VIO |
| 0 | 1 | 0 | Vdac |
| 1 | 0 | 1 | RxIn_VIO |
| 1 | 1 | 1 | RxIn_VIO |

#### RX CTLE

Figure 412 Block diagram of RX CTLE

Table 415. RX CTLE pin list

| Pin Names | Type | Power Domain | Clock Domain | Description |
| --- | --- | --- | --- | --- |
| VDD | PWR | VDD | N/A | PHY core power |
| VSS | PWR | N/A | N/A | Shared ground |
| ana_en | Input | VDD | Async | Active high to enable Rx analog part |
| inp | Input | VCCIO | Async | Positive input, connect to attenuator output |
| Vdac | Input | VCCIO | Async | Negative input, connect to voltage reference |
| CtleEnBuf | Input | VDD | Async | Active high to enable CTLE, nonfunctional pin |
| DCgain11b | Input | VDD | Async | Active low to adjust DCgain |
| DCgain1b | Input | VDD | Async | Active low to adjust DCgain |
| DCgain0b | Input | VDD | Async | Active low to adjust DCgain |
| ACgain1b | Input | VDD | Async | Active low to adjust ACgain |
| ACgain0b | Input | VDD | Async | Active low to adjust ACgain |
| vbiasp | Input | VDD | Async | Bias voltage (Internal signal)vbiasp = 0 when RxVbias = 1 |
| vbiasp_a0 | Input | VDD | Async | Bias voltage (Internal signal)vbiasp = 0 when RxVbias = 1 |
| vbiasp_a1 | Input | VDD | Async | Bias voltage (Internal signal)vbiasp = 0 when RxVbias = 1 |
| vbiasp_vcm_adj | Input | VDD | Async | Bias voltage to adjust output common mode voltage |
| outp | Output | VDD | N/A | Positive output with analog voltage level |
| outn | Output | VDD | N/A | Negative output with analog voltage level |

Table 46: RX CTLE truth table

| **RxEn** | **RxLbEn** | **ana_en** | **vpbias*** | **Vdac** | **inp** | **outp/outn** |
| --- | --- | --- | --- | --- | --- | --- |
| **0** | **0** | **0** | **X** | **X** | **X** | **1/1** |
| **1** | **0** | **1** | **1** | **X** | **X** | **X** |
| **1** | **0** | **1** | **0** | **0** | **0** | **X** |
| **1** | **0** | **1** | **0** | **0** | **1** | **1/0** |
| **1** | **0** | **1** | **0** | **1** | **0** | **0/1** |
| **1** | **0** | **1** | **0** | **1** | **1** | **1/0** |
| **X** | **1** | **0** | **X** | **X** | **X** | **1/1** |

Table 47. RX CTLE DC gain control description

| RxCtleEn | DCgain11b | DCgain1b | DCgain0b | Description | Notes |
| --- | --- | --- | --- | --- | --- |
| 0 | - | - | - | CML mode |  |
| 1 | 0 | 0 | 0 | Rs = 500 Ohm |  |
| 1 | 1 | 0 | 0 | Rs = 857 Ohm |  |
| 1 | 1 | 1 | 0 | Rs = 1500 Ohm |  |
| 1 | 1 | 1 | 1 | Rs = 2000 Ohm |  |

Table 48. RX CTLE AC gain control description

| ACgain1b | ACgain0b | Description | Notes |
| --- | --- | --- | --- |
| 0 | 0 | Rai = 3770 Ohm | Max Res |
| 0 | 1 | Rai = 2262 Ohm |  |
| 1 | 0 | Rai = 754 Ohm |  |
| 1 | 1 | Rai = 665 Ohm | Min Res |

### RXCKTRK Analog block (RXCK_ANA)

This cell represents the analog front end for rx. It included ESD, attenuator, VGA and CML2CMOS circuitry. This cell needs to be black boxed in equivalence check. It needs its own hierarchy and must be pin matched with circuit.

#### RXCKTRK Attenuator

Table 416 Truth table of RXCKTRK attenuator

| RxLbEn | RxEn | attms_en | attlb_en | OUT |
| --- | --- | --- | --- | --- |
| 0 | 0 | 1 | 0 | RxIn_VIO |
| 0 | 1 | 1 | 0 | RxIn_VIO |
| 1 | 0 | 1 | 0 | RxIn_VIO |
| 1 | 1 | 0 | 1 | LbDin |

#### RXCKTRK VGA

Figure 413 Block diagram of VGA

Table 417 RXCKTRK VGA pin list

| Pin Names | Type | Power Domain | Clock Domain | Description |
| --- | --- | --- | --- | --- |
| VDD | PWR | VDD | N/A | PHY core power |
| VSS | PWR | N/A | N/A | Shared ground |
| ana_en | Input | VDD | Async | Active high to enable AFE |
| inp | Input | VDD | Async | Positive input, connect to Attenuator output |
| Vdac | Input | VDD | Async | Negative input, connect to voltage referent |
| vbiasp | Input | VDD | Async | Bias voltage (Internal signal)vbiasp* = 0 when RxVbias = 1 |
| vbiasp_a0 | Input | VDD | Async | Bias voltage (Internal signal)vbiasp* = 0 when RxVbias = 1 |
| vbiasp_a1 | Input | VDD | Async | Bias voltage (Internal signal)vbiasp* = 0 when RxVbias = 1 |
| outp | Output | VDD | N/A | Positive output with analog voltage level |
| outn | Output | VDD | N/A | Negative output with analog voltage level |

Table 418 RXCKTRK VGA truth table

| RxEn | ana_en | vpbias* | Vdac | inp | outp/outn |
| --- | --- | --- | --- | --- | --- |
| 0 | 0 | X | X | X | 1/1 |
| 1 | 1 | 1 | X | X | X |
| 1 | 1 | 0 | 0 | 0 | X |
| 1 | 1 | 0 | 0 | 1 | 1/0 |
| 1 | 1 | 0 | 1 | 0 | 0/1 |
| 1 | 1 | 0 | 1 | 1 | 1/0 |

#### RXCKTRK CML2CMOS

Figure 414 Block diagram of RXCKTRK CML2CMOS

Table 419 RXCKTRK CML2CMOS pin list

| Pin Names | Type | Power Domain | Clock Domain | Description |
| --- | --- | --- | --- | --- |
| VDDREG | PWR | VDDREG | N/A | Power generated from VREG |
| VSS | PWR | N/A | N/A | Shared ground |
| cml2cmos_en | Input | VDDREG | Async | Enable CML2CMOS circuit |
| ctle_en | Input | VDDREG | Async | Nonfunctional pin. It is used to enable CTLE |
| inp | Input | VDDREG | Async | Positive input, connect to VGA |
| inn | Input | VDDREG | Async | Negative input, connect to VGA |
| outcml2cmos | Output | VDDREG | N/A | Output with CMOS level |

Table 420 RXCKTRK CML2CMOS truth table

| **Rx****Trk****En** **(*********)** | **RxL****b****En****(*)** | **R****xEn** **(*****)** | **cml2cmos_en** | **inp** | **inn** | **outcml2cmos** |
| --- | --- | --- | --- | --- | --- | --- |
| **1** | **X** | **X** | **0** | **X** | **X** | **0** |
| **X** | **X** | **0** | **0** | **X** | **X** | **0** |
| **0** | **0** | **1** | **1** | **0** | **1** | **0** |
| **0** | **0** | **1** | **1** | **1** | **0** | **1** |
| **0** | **1** | **1** | **1** | **0** | **1** | **0** |
| **0** | **1** | **1** | **1** | **1** | **0** | **1** |

* RXCKTRK top pins affect control of CML2CMOS

### RXCKTRK Clock gater

Figure 415 High level of RXCKTRK Clock gater

Table 421 RXCKTRK Clock gater pin list

| Pin Names | Type | Power Domain | Clock Domain | Description |
| --- | --- | --- | --- | --- |
| clkin | Input | VDD | clkin | Input clock |
| en | Input | VDD | Async | Clock gater enable, synchronized by clkin |
| se | Input | VDD | Async | Clock gater enable, asynchronous enable |
| pause | Input | VDD | Async | Clock pause signal, synchronized by clkin |
| clkout | Output | VDD | clkin | Clock output |

Figure 416 Operation waveform of the synchronized clock enable and clock pause

Figure 417 Operation waveform of asynchronous enable

### RXCMOS

This cell receives data for Async mode. Maximum speed is 400Mhz

Figure 418 Block diagram of RXCMOS

Table 422 RXCMOS pin list

| Pin Names | Type | Power Domain | Clock Domain | Description |
| --- | --- | --- | --- | --- |
| VDD | PWR | VDD | N/A | PHY core power |
| VSS | PWR | N/A | N/A | Shared ground |
| RxAsyncEn | Input | VDD | Async | Active high to enable RXCMOS |
| RxIn_VIO | Input | VCCIO | Async | Positive input, connect to IO PAD |
| Vdac | Input | VCCIO | Async | Negative input, connect to Voltage reference |
| vbiasp | Input | VDD | Async | Bias voltage |
| RxDatAsync | Output | VDD | N/A | Output with CMOS level |

Table 423 RXCMOS truth table

| **Rx****AsyncEn** | **vpbias** | **Vdac** | **RxIn_VIO** | **RxDatAsync** |
| --- | --- | --- | --- | --- |
| 0 | X | X | X | 0 |
| 1 | 1 | X | X | X |
| 1 | 0 | 0 | 0 | X |
| 1 | 0 | 0 | 1 | X |
| 1 | 0 | 1 | 0 | 0 |
| 1 | 0 | 1 | 1 | 1 |

### DAC

- DAC is used to generate reference input voltage (Vref) for the receiver. Below table shows DAC cell used in rx
Table 424 DAC setting

| **RxDacSelBuf****[7****:0****]** | **Vdac** | **Note** |
| --- | --- | --- |
| 0000-0000 | ~0V | Min voltage |
| 0111-1111 | ~VCCIO/2 | Default voltage |
| 1111-1111 | ~VCCIO | Max voltage |

#### DAC Training algorithm

DAC Training algorithm is used to find optimal DAC code value (OptVrefCode) for each RX cell as well as RXCKTRK. The flowchart is described in Figure 419 and 0

Figure 419 VDAC training flow for data path

### RX FIFO

Figure 420 Block diagram of RX FIFO 16-bit version

Figure 421 Operation waveform of RX mission mode

### Sampler offset compensation

Sampler offset compensation algorithm is described as below.

- Set RxOffsetEn = 1, RxEn = 1, RxOffSetCal = 1
- For each sampler, set initial code of RxOffsetSel_*[6:0] = 7d’0, monitor the value of RxData[*] corresponding to each sampler: - If RxData[*] =0, sweep RxOffsetSel_*[6:0] from 7d’0 to 7d’63. - If RxData[*] =1, sweep RxOffsetSel_*[6:0] from 7d’64 to 7d’127. - The sweeping sequence of RxOffsetSel_*[6:0] can be carried out in two phase: coarse step and fine step. At beginning, sweep RxOffsetSel_*[6:0] by coarse step until the logic of RxData[*] is flipped (0 to 1 or 1 to 0). In case the RxData[*] do not flip during coarse step sweeping, return the RxOffsetSel_*[6:0] = 7d’0. From the flipped offset code, sweep backward with fine step=1 until the RxData[*] is flipped again. Record this code of RxOffsetSel_*[6:0] to CSR.
- After offset compensation is done, users must set RxOffsetEn = 1, RxOffsetCalEn = 0 and program RxOffsetSel_* in all RX operation mode.
The training sequence can be simplified by the flow as below:

Figure 422 Sampler offset training sequence

### Lane-to-lane deskew

RX lane-to-lane deskew is an additional step in case of the partner PHY TX is not have enough deskew range. This step must be executed after TX lane-to-lane deskew and after RX phase mismatch compensation.

The algorithm is described as the steps below:

- Proceed 2D eye search, find the minimum and maximum edge of eye.
- Only compare Pass/Fail of data of one clock phase (e.g. clock phase 0).
- Use the maximum edge found in step 1.
- Set BDLs to 0.
- Send N consecutive data transfers and read the data check.
- For any lane that passes all data transfers, update its four bit delays (BDLs) with the current bit delay.
- For any lane that fails any data transfer, set its sticky fail (error) status flag. All lanes that have their sticky error flags set will no longer have their bit delays updated.
- If any lane passes, increment the bit delay and go to Step 4.
- If all lanes have their sticky error flags set, then the RX deskew values have been found.
### Phase mismatch compensation

With quadrature clocking architecture, each phase samples one data beat: CK0/90/180/270 captures data0/1/2/3. The clock phase mismatch may cause a wrong data sampling or degrade link margin. Therefore, the phase correction is important.

Phase correction algorithm is described as below. This algorithm requires to have capability of PASS/FAIL comparison per data beat of each data lane.

- Proceed 2D eye search of each data lance, find the minimum and maximum edge.
- Use the maximum edge found in step 1
- Set BDLs to the current value found in RX lane-to-lane deskew.
- Send N consecutive data transfers and read the data check.
- For any RX data beat that passes, update its BDL with the current bit delay
- For any RX data beat that fails, set its sticky fail (error) status flag. All data beats that have their sticky error flags set will no longer have their bit delays updated
- If any RX data beat passes, increment the bit delay and go to Step 4.
- If all RX data beats have their sticky error flags set, then the phase deskew values have been found
Below is a picture that demonstrates some scenarios:

Figure 423 Clock calibration examples

### Optimal analog configuration training

The optimal analog configuration training is applied for RX Data only. The RXCKTRK uses the default setting which is defined by CSR. This training step is put after 2D Data Eye Training step. For RTL implementation, it is required to have a CSR to skip or not skip any steps. Optimal analog configuration training is described as below:

- From 2D Data Eye Training, choose optimal setting for RxDacSel[7:0]
- Set RxCurrAdj[1:0] by:
- *if (RxCurrAdj_train_skip == 0) {*
- *RxCurrAdj[1:0] = 2’b11*
*} else { *

*RxCurrAdj[1:0] = **u**ser defined *

*}*

- Proceed with the loop below:
- *f**or each *****ACgain configuration** sweep**, proceed**:**{*
*For each ******DCgain config**uration sweep, proceed**:**{*

*Proceed 1D eye search (sweep LCDL)*

*}*

*}* Store the best combination of ACgain configure and DCgain configure, which produces the maximum eye width *ACgain configuration:

*if(RxACgain_train_skip == 0)** **{** **// sweep has 5 configures//*

- *RxACgain[1:0] = 2’b11, **Rx**VcmAdj** = 1’b**0*
- *RxACgain[1:0] = 2’b10, **RxVcmAdj **= 1’b**0*
- *RxACgain[1:0] = 2’b01, **RxVcmAdj **= 1’b**0*
- *RxACgain[1:0] = 2’b00, **RxVcmAdj **= 1’b**0*
- *RxACgain[1:0] = 2’b00, **RxVcmAdj **= 1’b**1*
- *RxACgain[1:0] = 2’b0**1**, RxVcmAdj = 1’b1*
- *RxACgain[1:0] = 2’b**10**, RxVcmAdj = 1’b1*
- *RxACgain[1:0] = 2’b**11**, RxVcmAdj = 1’b1*
* **}** else {** // don’t sweep, return the user defined //*

*RxACgain[1:0] = **user defined*

*RxVcmAdj = **user defined*

* }*

**DCgain configuration:

*if(RxDCgain_train_skip == 0){** **// sweep has 5 configures //*

- *RxCtleEn = 1’b1, RxDCgain[1:0] = 2’b00*
- *RxCtleEn = 1’b1, RxDCgain[1:0] = 2’b01*
- *RxCtleEn = 1’b1, RxDCgain[1:0] = 2’b10*
- *RxCtleEn = 1’b1, RxDCgain[1:0] = 2’b11*
- *RxCtleEn = 1’b0, RxDCgain[1:0] = 2’b00*
* } else {** // don’t sweep, return the user defined //*

*RxCtleEn =** user defined*

*RxDCgain[1:0]** = user defined*

* }*

- Set RxCtleEn, RxDCgain[1:0] and RxACgain[1:0] from step 2
- *if (RxCurrAdj_train_skip == 0){*
- *For each **configuration below**, proceed 1D eye search (sweep LCDL):*
- *RxCurrAdj**[1:0]** = 2’b11*
- *RxCurrAdj**[1:0]** = 2’b10*
- *RxCurrAdj**[1:0]** = 2’b01*
- *RxCurrAdj**[1:0]** = 2’b00*
- *Store configuration which produces maximum eye width*
* **} else {*

* **RxCurrAdj[1:0] = **u**ser defined*

* **}*

- Optimal analog configuration is combination of RxCtleEn, RxDCgain[1:0], RxNegCEn and RxACgain[1:0] from step 2, RxCurrAdj[1:0] from step 3
After optimal analog configuration training is done, it is required to do 2D Data Eye Training step again to get the optimal VREF corresponding to optimal analog configuration.

### Clock duty cycle and I/Q calibration

#### High level connection

In DW level, the recommended connection is shown in Figure 424. The ck0, ck90, ck180 and ck270 are connected to clk_inp0, clk_inp1, clk_inn0 and clk_inn1 of cell DCD respectively.

Figure 424 Recommended connection of RXCKTRK and DCD

#### Calibration sequence

Figure 425 shows the calibration sequence. User must configure the DCD mode corresponding to each step.

The forwarding clock from partner die is quired. And this calibration is processed after the partner die completes all its TX clock calibration.

Figure 425 Clock duty cycle and I/Q calibration sequence

##### Clock duty cycle calibration flow

Figure 426 RXCKTRK clock duty cycle calibration flow

##### I/Q phase calibration

This step requires the partner die to have a capability to adjust the delay of TXCKP and TXCKN.

Figure 427 I/Q Phase calibration flow

### Clock and data recovery (Not supported)

Clock and data recovery (CDR) is an additional feature that auto monitoring the phase relationship between data and strobe clock. This feature is for from 24Gpbs and higher. based on Alexander Phase Detector,Figure 428, where CK takes three consecutive samples, S1-S3. If the falling edge of CK is “late” with respect to the rising edge of Din, then S1 ≠ S2 = S3. On the other hand, if CK is “early” if S1 = S2 ≠ S3.

Figure 428 Clock and data recovery concept

S1 and S2 must be stored before S3 is available so that three samples are aligned in time for proper comparison. So, there is additional “retimer” for this purpose.

The traditional Alexander Phase Detector requires clock frequency to be the same as data rate, while our RX only have 4-phase clock and frequency is ¼ data rate. To fit with our RX architecture, we use CK0 to samples Q1, CK45 samples Q2 and CK90 samples S2. There is 1-bit phase interpolator to generate CK45 from CK0 and CK90. There are three “retimer” flip-flops that provide three samples at the same time. The final architecture is shown in Figure 429.

There are four 10-bit phase accumulators that receive the signal “Early” and “Late” from RX. The accumulator is basically a form of counter. Any rising edge of “Early”, the counter is increase by 1. And one the other hand, any rising edge of “Late” causes the counter to be decreased by 1.

The upper 6 bits of the phase accumulators are used to program the RX BDL. The initial value of the accumulator:

- [3:0] = 4’b0
- [9:4] is from Phase mismatch calibration step.
Figure 429 CDR architecture

Figure 430 CDR output waveform for case clock "late"

Figure 431 CDR output waveform for case clock "early"

### Signal Integrity Monitor (SIM)

Signal Integrity Monitor is designed to measure the link margin of Die-2-Die interface. Within one clock period four data bits are transmitted on the same data lane. Each bit is synchronized to a 90 degrees phase shift of the clock. To determine the signal integrity of the interconnect, monitoring a single phase of the data capture will be adequate since the same path is used for all other phases. Any of the phases can be used for monitoring. In this implementation the clk270 is chosen for monitoring.

The SIM unit uses one clock as Monitor clock which its delay can be adjusted. At every delay step, the input data is sampled by the Monitor clock and the output is compared against the actual data of clock phase 270. The comparison result is read out by a scan chain. By repeating this sequence, we can build the eye width and extract the link margin information.

In upper level, RxSimSi and RxSimSo of RXs will be connected into a chain: RxSimSi of the first RX will be connected to controller and its RxSimSo will be connected to RxSimSi of the adjacent RX and so on.

The SIM circuit uses the sampler, so offset calibration will be done first.

The SIM clock also needs to calibrate first. Refer to section 5.1.3.3 SIM clock calibration

Figure 432 High level block diagram of SIM circuit

The SIM unit has two operation modes:

- Measure mode
In this mode, SIM unit performs data sample and compare operation. The sequence to put SIM in measure mode:

- RxSimSclk is gated.
- RxSimResetn is asserted to clear the previous measurement result, then deassert it.
- Program delay of RxSimClk (LCDLSIM).
- Set RxSimMode to zero.
- Enable RxSimClk (LCDLSIM gater).
- Wait a programmable number of PhyClk cycles to make the measurement.
- Set RxSimMode to 1 to complete measurement phase and ready for capture phase.
- Wait few cycles of RxSimClk to complete RxSimMode synchronization.
- Disable RxSimClk (LCDLSIM gater).
The measurement period is manually control through the configuration register. When any data mismatch occurs, the measurement result is 1 and hold in final flop waiting for read out, ignore all other data bits.

Figure 433 Measure mode operation waveform

- Collect mode
In this mode the clock is switched to the serial clock input and the status bits are serially shifted out to the controller. The controller generates exact number of clock pulses to shift data from all the SIMUs.

The SIM operates in a sequence of measure, followed by collect phase, repeatedly.

## dwc_ucie2phy_rxodt

### Overview

dwc_ucie2phy_rxodt is a replica version of RX on-die termination resistor. It is used for impedance calibration in MMPL block.

Table 425 RXODT cell list

| # | Cell name | Description |
| --- | --- | --- |
| **1** | dwc_ucie2phy_rxodt_ns | Support UCIe-S, NS PHY orientation |
| **2** | dwc_ucie2phy_rxodt_ew | Support UCIe-S, EW PHY orientation |

### Block diagram

Figure 434 Block diagram of termination

### Pin description

Table 426 dwc_ucie2phy_rxodt pin description

| **Pin Names** | **Type** | **Power Domain** | **Bit Width** | **Clock Domain** | **Description** |
| --- | --- | --- | --- | --- | --- |
| VDD | Input | VDD |  | N/A | PHY core power |
| VSS | Input | VSS |  | N/A | Shared ground |
| VCCIO | Input | VCCIO |  | N/A | PHY IO power |
| RxIn_VIO | Input | VCCIO |  | DQS CLK | Analog strobe input from pad; No requires CDM protection in MSCTRL |
| RxTermResCode[5:0] | Input | VDD | 6 | Async | Switchable resistance leg. Used to calibrate for 50Ohm |
| RxTermGdEn | Input | VDD |  | Async | Termination enables. Use as default resistance leg. |

### RX On Die Termination Specification

It’s available in rx_std, rxcktrk_std for UCIe-S

| **Parameter** | **M****in** | **Typ** | **M****ax** | **Unit** |
| --- | --- | --- | --- | --- |
| Rx Input Impedance | 45 | 50 | 55 | Ohm |
| Impedance Step Size | - | - | 1 | Ohm |
| RX Min range |  |  | 40 | Ohm |
| Rx Max range | 60 |  |  | Ohm |

Default legs -] "RxTermGdEn" is used to turn on 10 shunt connected legs by default (the number of 20 is chosen base on the early calculation and may be change later)

Switchable legs -] “RxTermResCode[5:0]” are used to calibrate for 50Ohm termination impedance at DC

Tune range implementation :

- “RxTermGdEn” controls 10 shunt-connected unit cell
- “RxTermResCode[5:2]” control 8, 4, 2, 1 shunt-connected unit cells.
- “RxTermResCode[1]” controls “1” doubly resistive unit cell.
- “RxTermResCode[0]” controls “1” quarterly-resistive unit cell.
| **Parameter** | **M****in** | **Typ****(*)** | **M****ax** |
| --- | --- | --- | --- |
| RxTermResCode[5:0] | 6’b001100 | 6’b011100 | 6’b101010 |
| RxTermGdEn | 1’b1 |  |  |

## 4.8 RTL and timing constraints

### RX, RX_STD

| Parameter | Value | Macro | Description |
| --- | --- | --- | --- |
| t_rx_enabling | 50 ns | rx | This is RxEn signal in rx. After asserting RxEn signal coming to rx, we should wait for total of t_rx_enabling to consider valid output signal (In all Testchip version, this parameter is 500ns) |
| t_dac_settling | 50 ns | rx | The time is measured from DAC power supply crossing 50% of VCCIO to VDAC output voltage stabilizing within +/-10% of its stable step value (see figure 3-6) |
| t_dac_step_settling | 20 ns | rx | The time we should wait after increasing/decreasing one DAC code until Vdac output voltage stabilizing within +/-10% of its stable step value (see figure 3-7) |
| t_dac_max_step_range_settling | 50ns | rx | The time we should wait after changing DAC code from 0 to 255 (or 255 to 0) until Vdac output voltage stabilizing within +/-10% of its stable step value (see figure 3-8) |
| t_RxCtleEn_settling | 5ns | rx | This is common signal in DW, distributing to all RXs. After asserting RxCtleEn signal, we should wait for t_RxCtleEn_settling before considering rx/rxcktrk cells that are ready to receive input data |
| t_RxDCgain_settling | 5ns | rx | This is common signal in DW, distributing to all RXs. After asserting RxDCgain signal, we should wait for t_RxDCgain_settling before considering rx/rxcktrk cells that are ready to receive input data |
| t_settling_time RxOffsetEn | 100ns | rx | Measure the settling time when RxOffsetEn is ramping up (on). |
| t_settling_time RxOffSetCalEn | 5ns | rx | Measure the settling time when RxOffSetCalEn is ramping up (on). |
| t_settling_time_offset_code | 20ns | rx | Measure the settling time of Offgen for all step codes |
| t_RxACgain_settling | 5ns | rx | This is common signal in DW, distributing to all RXs. After asserting RxACgain signal, we should wait for t_RxACgain_settling before considering rx/rxcktrk cells that are ready to receive input data |
| t_RxCurrAdj_settling | 5ns | rx | This is common signal in DW, distributing to all RXs. After asserting RxCurrAdj signal, we should wait for t_RxCurrAdj_settling before considering rx/rxcktrk cells that are ready to receive input data |
| t_RxNegCEn_settling | 5ns | rx | This is common signal in DW, distributing to all RXs. After asserting RxNegCEn signal, we should wait for t_RxNegCEn_settling before considering rx/rxcktrk cells that are ready to receive input data |
| t_RxAsyncEn_settling | 500ps(Initial value – will be updated) | rx | This is RxAsyncEn signal in rx. After asserting RxAsyncEn signal coming to rx, we should wait for total of t_RxAsyncEn_settling to consider valid output signal (This is initial value only, will be updated) |
| t_LbEn_settling | TBD – Loopback is dropped in Dec TC | rx | This is LbEn signal. After toggling this signal, we should wait for t_LbEn_settling before considering rx/rxcktrk cells that are ready to receive input data |

### RXCKTRK, RXCKTRK_STD

| Parameter | Value | Macro | Description |
| --- | --- | --- | --- |
| t_rx_enabling | 50 ns | rxcktrk | This is RxEn signal in rx. After asserting RxEn signal coming to rx, we should wait for total of t_rx_enabling to consider valid output signal (In all Testchip version, this parameter is 500ns) |
| t_dac_settling | 50 ns | rxcktrk | The time is measured from DAC power supply crossing 50% of VCCIO to VDAC output voltage stabilizing within +/-10% of its stable step value (see figure 3-6) |
| t_dac_step_settling | 20 ns | rxcktrk | The time we should wait after increasing/decreasing one DAC code until Vdac output voltage stabilizing within +/-10% of its stable step value (see figure 3-7) |
| t_dac_max_step_range_settling | 50ns | rxcktrk | The time we should wait after changing DAC code from 0 to 255 (or 255 to 0) until Vdac output voltage stabilizing within +/-10% of its stable step value (see figure 3-8) |
| t_RxCtleEn_settling | 5ns | rxcktrk | This is common signal in DW, distributing to all RXs. After asserting RxCtleEn signal, we should wait for t_RxCtleEn_settling before considering rx/rxcktrk cells that are ready to receive input data |
| t_RxDCgain_settling | 5ns | rxcktrk | This is common signal in DW, distributing to all RXs. After asserting RxDCgain signal, we should wait for t_RxDCgain_settling before considering rx/rxcktrk cells that are ready to receive input data |
| t_RxACgain_settling | 5ns | rxcktrk | This is common signal in DW, distributing to all RXs. After asserting RxACgain signal, we should wait for t_RxACgain_settling before considering rx/rxcktrk cells that are ready to receive input data |
| t_RxCurrAdj_settling | 5ns | rxcktrk | This is common signal in DW, distributing to all RXs. After asserting RxCurrAdj signal, we should wait for t_RxCurrAdj_settling before considering rx/rxcktrk cells that are ready to receive input data |
| t_RxNegCEn_settling | 5ns | rxcktrk | This is common signal in DW, distributing to all RXs. After asserting RxNegCEn signal, we should wait for t_RxNegCEn_settling before considering rx/rxcktrk cells that are ready to receive input data |
| t_RxAsyncEn_settling | 500ps(Initial value – will be updated) | rxcktrk | This is RxAsyncEn signal in rxcktrk. After asserting RxAsyncEn signal coming to rxcktrk, we should wait for total of t_RxAsyncEn_settling to consider valid output signal (This is initial value only, will be updated) |
| t_LbEn_settling | TBD – Loopback is dropped in Dec TC | rxcktrk | This is LbEn signal. After toggling this signal, we should wait for t_LbEn_settling before considering rx/rxcktrk cells that are ready to receive input data |

### IDDQ Measurement

Figure 435 Setting for IDDQ measurement

| Macro | Pin | Value | Description |
| --- | --- | --- | --- |
| RX*/RXCKTRK* | RxEn | 0 | Disable RX |
|  | RxAsyncEn | 0 | Disable RX asyn |
|  | RxDacSel | 0 | Disable VDAC |
|  | RxOccEn | 0 | Disable DFT |

### Burn-in Test Recommendation

To ensure maximum toggling of internal nodes during burn-in test, the recommendation is to run a combination of mission mode and loopback mode.

# RX Calibration

## dwc_ucie2phy_rxcal

In system, there are two clock receivers that receive the forwarding clock (BP_CKP and BP_CKN) from the partner die. The phase (differential or quadrature) is defined by UCIe specification.

In the differential forwarding clock mode, the clock receivers convert it to quadrature clock (ck_0/90/180/270) by a clock divider. However, the clock gater enable signal synchronizer may cause the order mismatch.

dwc_ucie2phy_rxcal16b is used to detect the order mismatch between ck_0 and ck_90. When the mismatch is detected, the output Early or Late goes high. The digital logic observes the output and then correct the order by sending a clock pause signal to BP_CKP receiver.

dwc_ucie2phy_rxcal16b is also used for FIFO pointer calibration.

dwc_ucie2phy_rxcal16bsim has additional feature for SIM clock calibration. It is applicable for the PHY with SIM.

Table 51 rxcal cell list

| # | Cell name | Description |
| --- | --- | --- |
| **1** | dwc_ucie2phy_rxcal16b_ns | Support UCIe-A/S, NS PHY orientation |
| **2** | dwc_ucie2phy_rxcal16b_ew | Support UCIe-A/S, EW PHY orientation |
| **3** | dwc_ucie2phy_rxcal16bsim_ns | Support UCIe-A/S with SIM, NS PHY orientation |
| **4** | dwc_ucie2phy_rxcal16bsim_ew | Support UCIe-A/S with SIM, EW PHY orientation |

### Block diagram

Figure 51 The high-level block diagram of rxcal16b

Figure 52 Block diagram of phase detector

### Pin description

Table 52 Pin description of rxcal16b

| Pin Names | Direction | Type | Power Domain | Clock Domain | Description |
| --- | --- | --- | --- | --- | --- |
| VDD | Input | Power | VDD | - | PHY core power |
| VSS | Input | Ground | VSS | - | Shared ground |
| PhyClk | Input | Clock | VDD | PhyClk | PHY clock |
| RxClkIn_0 | Input | Clock | VDD | RxClkIn_0 | Clock for sampler phase 0 |
| RxClkIn_90 | Input | Clock | VDD | RxClkIn_90 | Clock for sampler phase 90 |
| RxClkIn_180 | Input | Clock | VDD | RxClkIn_180 | Clock for sampler phase 180 |
| RxClkIn_270 | Input | Clock | VDD | RxClkIn_270 | Clock for sampler phase 270 |
| RxResetn[1:0] | Input | Digital | VDD | Async | Async reset, active low RxResetn[0]: RxClk domain RxResetn[1]: PhyClk domain |
| RxRdPtr[1:0] | Input | Digital | VDD | PhyClk | Read pointer value |
| RxSe | Input | Digital | VDD | PhyClk | Scan enable |
| RxSi | Input | Digital | VDD | PhyClk | Scan input |
| CalDone | Output | Digital | VDD | RxClkIn_270 | Calibration done. Unused pin, tied low internally |
| CalOut[11:0] | Output | Digital | VDD | PhyClk | CalOut[3:0]: Calibration output CalOut[10:4]: unused pins, tied low internally CalOut[11]: output of DFT scan chain |
| RxCknEarly | Output | Digital | VDD | Async | RxClkIn_90 is earlier than RxClkIn_0/180. Indicate that the BP_CKN clock gater is enabled 1 cycle earlier than BP_CKP |
| RxCknLate | Output | Digital | VDD | Async | RxClkIn_90 is later than RxClkIn_0/180. Indicate that the BP_CKN clock gater is enabled 1 cycle later than BP_CKP |
| RxSimClk | Input | Clock | VDD | RxSimClk | SIM clock |
| RxSimDat[3:0] | Output | Digital | VDD | RxSimClk | Phase detector output |

### Operation

#### FIFO pointer calibration

//depot/products/ucie/common/dev_2.0/arch/doc/dwc_uciephy_architecture_specification.pdf

#### Phase detector

dwc_ucie2phy_rxcal contains two phase detectors to compare the phase of RxClkIn_0 versus RxClkIn_90 and RxClkIn_90 versus RxClkIn_180. The concept is:

- When no order mismatch: the RxClkIn_90 must be located somewhere between RxClkIn_0 and RxClkIn_180.
- When CKN is enabled 1 cycle earlier than CKP: the RxClkIn_90 is earlier than RxClkIn_0 and RxClkIn_180
- When CKN is enabled 1 cycle later than CKP: the RxClkIn_90 is later than RxClkIn_0 and RxClkIn_180
Figure 53 Operation waveform when no clock order mismatch

Figure 54 Operation waveform when CKN is enabled earlier than CKP

Figure 55 Operation waveform when CKN is enabled later than CKP

#### SIM clock calibration

There is a flop-based phase detector for SIM clock calibration. In PHY top level, SIM clock source is RxClk180 and its latency can be adjustable by a LCDL. The SIM clock and RX mission clock are distributed by the same clock tree but the number of components is different, so their edge is not matched over PVT. Figure 56 shows the possible SIM clock position before calibration. In this application, we only care rising edge.

The phase detector relies on CMOS flip-flop (with very low setup/hold time requirement) which input data is clk180 (after RX BDL) and clock is RxClkSim. The SIM clock delay is increased until RxSimDat changes from 0 to 1.

It is recommended to have a CSR to define the offset value. The final LCDL code can be added or subtracted by amount of offset value.

Figure 56 SIM clock before calibration

Figure 57 SIM clock after calibration

### DFT

#### Setting

None

#### Scan chain

Table 53 Scan chain information of RXCAL

| **Scan chain No.** | **DFT input Clock** | **DFT input data** | **DFT input enable** | **DFT output** | **Sync clock edge** | **Length** | **Description** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | PhyClk | RxSi | RxSe | CalOut[11] | rising | 16 | Scan chain in RXCAL |

### RTL and Timing requirement

There is no special requirement for DFT, IDDQ measurement, burn-in test and anti-aging.

# Sideband Receiver

## dwc_ucie2phy_rxsb

### Overview

dwc_ucie2phy_rxsb is a CMOS inverter-based receiver, able to receive full-speed full-rail signals on the uBumps. It is intended to be used in sideband region for the sideband uBump. The maximum data rate is 2Gbps.

The cell list is shown in Table 61. They have the same function and pin interface.

Table 61 rxsb cell list

| # | Cell name | Description |
| --- | --- | --- |
| **1** | dwc_ucie2phy_rxsb | Support both UCIe-A/S, and both NS and EW PHY orientation |

### Block Diagram

Figure 61 Block diagram of rxsb

### Pin Description

| **Pin Names** | **Type** | **Power Domain** | **Bit Width** | **Clock Domain** | **Description** |
| --- | --- | --- | --- | --- | --- |
| VDD | Input | VDD |  | N/A | PHY core power |
| VCCAON | Input | VCCAON |  | N/A | PHY VCCAON power |
| VSS | Input | VSS |  | N/A | Shared ground |
| RxIn_VAON | Input | VCCAON |  | CLK | Analog strobe input from pad; requires CDM protection |
| PwrOk_VAON | Input | VCCAON |  | Async | Power on input signal |
| RxEn | Input | VDD |  | Async | RX enable |
| LbEn | Input | VDD |  | Async | Core loopback enable |
| LbDin | Input | VDD |  | Async | Core loopback positive clock |
| RxReserved[1:0] | Input | VDD | 2 | Async | Reserved pins |
| RxOut | Output | VDD |  | Async | RX Output |

### Operation modes

#### Mission Mode

dwc_ucie2phy_rxsb is designed to receive data or clock signal. The maximum data rate is 2Gbps (2GHz clock).

Table 62: Logic Function for rxsb receiver

| PwrOk_VAON | RxEn | LbEn | RxOut |
| --- | --- | --- | --- |
| 0 | x | 0 | x |
| 0 | x | 1 | x |
| 1 | 0 | 0 | 0 |
| 1 | 1 | 0 | follows RxIn_VAON. |
| 1 | x | 1 | Follows LbDin |

#### Loopback mode

The core loopback function enabled internal loopback (not going through the pads).

Receivers has an enable input called LbEn. When this is asserted, the receivers function as described below:

- dwc_ucie2phy_rxsb: the LbDin input is selected as the (asynchronous) output
#### Idle mode

In this mode, the configuration is the same as the mission, but the input PAD is static 0 or 1.

#### Standby mode

In this mode, the receiver is disabled by setting RxEn to 0. The input PAD is static 0 or 1.

#### DFT

Table 63: DFT Input Requirement for dwc_ucie2phy_rxsb

| **Input name** | **Bus width** | **Value** |
| --- | --- | --- |
| RxEn | 1 | 0 |

### IDDQ measurement

| Pin | Value | Description |
| --- | --- | --- |
| RxEn | 0 | Disable RX |

### Burn-in Test Recommendation

To ensure maximum toggling of internal nodes during burn-in test, the recommendation is to run a combination of mission mode and loopback mode.

# Simulation plan

Please refer to
