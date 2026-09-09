type EventHandler = (data: any) => void;

class EventBus {
  private handlers: Record<string, EventHandler[]> = {};

  on(event: string, handler: EventHandler) {
    if (!this.handlers[event]) this.handlers[event] = [];
    this.handlers[event].push(handler);
  }

  off(event: string, handler: EventHandler) {
    if (!this.handlers[event]) return;
    this.handlers[event] = this.handlers[event].filter(h => h !== handler);
  }

  emit(event: string, data?: any) {
    if (!this.handlers[event]) return;
    this.handlers[event].forEach(h => h(data));
  }
}

export const eventBus = new EventBus();
