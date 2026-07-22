#ifndef AGINTI_C12880_USB_H
#define AGINTI_C12880_USB_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef struct {
  uint32_t magic;
  uint32_t init_calls;
  uint32_t init_stage;
  uint32_t class_init_calls;
  uint32_t class_deinit_calls;
  uint32_t control_calls;
  uint32_t set_line_coding_calls;
  uint32_t get_line_coding_calls;
  uint32_t set_control_line_state_calls;
  uint32_t receive_packets;
  uint32_t receive_bytes;
  uint32_t transmit_requests;
  uint32_t transmit_completions;
  uint32_t last_control_command;
  uint32_t last_control_length;
  uint32_t last_bitrate;
} c12880_usb_diagnostics_t;

extern volatile c12880_usb_diagnostics_t g_aginti_c12880_usb_diag;

bool c12880_usb_init(void);
bool c12880_usb_busy(void);
int c12880_usb_transmit(const uint8_t *data, size_t bytes);
size_t c12880_usb_read(uint8_t *destination, size_t capacity);
uint32_t c12880_usb_rx_overruns(void);
void app_usb_tx_complete_isr(void);

#endif
