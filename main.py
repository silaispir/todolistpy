import heapq
from datetime import datetime
from collections import deque

class ToDoList:
    def __init__(self):
        """Başlangıçta veri yapılarını oluştur"""
        # Tüm görevleri saklamak için liste (List)
        self.tasks = []
        
        # Öncelik sırası için min-heap (Priority Queue)
        self.priority_queue = []
        
        # Geri alma işlemleri için stack (LIFO)
        self.undo_stack = deque()
        
        # Benzersiz ID için sayaç
        self.task_id_counter = 1

    def add_task(self, name, priority=3, due_date=None):
        """
        Yeni görev ekleme
        :param name: Görev adı
        :param priority: Öncelik (1-5 arası, 1 en yüksek)
        :param due_date: Son tarih (YYYY-AA-GG formatında)
        """
        # Eğer tarih verilmediyse bugünün tarihini al
        if due_date is None:
            due_date = datetime.now().strftime("%Y-%m-%d")
        
        # Görev sözlüğü oluştur
        task = {
            'id': self.task_id_counter,
            'name': name,
            'priority': priority,
            'due_date': due_date,
            'completed': False,
            'created_at': datetime.now()
        }
        self.task_id_counter += 1
        
        # Görevi listeye ekle
        self.tasks.append(task)
        
        # Öncelik kuyruğuna ekle (priority, eklenme sırası, task)
        heapq.heappush(self.priority_queue, (priority, task['id'], task))
        
        # Undo işlemi için kayıt oluştur
        self.undo_stack.append(('add', task['id']))
        
        print(f"✅ '{name}' görevi eklendi (ID: {task['id']})")

    def complete_task(self, task_id):
        """
        Görevi tamamlandı olarak işaretle
        :param task_id: Tamamlanacak görev ID'si
        """
        for task in self.tasks:
            if task['id'] == task_id:
                if not task['completed']:
                    # Undo için önceki durumu kaydet
                    self.undo_stack.append(('complete', task.copy()))
                    
                    # Görevi tamamlandı olarak işaretle
                    task['completed'] = True
                    print(f"🎉 '{task['name']}' görevi tamamlandı!")
                else:
                    print("⚠️ Bu görev zaten tamamlanmış")
                return
        
        print("❌ Görev bulunamadı!")

    def delete_task(self, task_id):
        """
        Görevi sil
        :param task_id: Silinecek görev ID'si
        """
        for i, task in enumerate(self.tasks):
            if task['id'] == task_id:
                # Undo işlemi için görevin kendisini kaydet
                self.undo_stack.append(('delete', task))
                
                # Görevi listeden kaldır
                deleted_task = self.tasks.pop(i)
                
                # Öncelik kuyruğunu güncelle
                self._rebuild_priority_queue()
                
                print(f"🗑️ '{deleted_task['name']}' görevi silindi")
                return
        
        print("❌ Görev bulunamadı!")

    def _rebuild_priority_queue(self):
        """Öncelik kuyruğunu yeniden oluştur"""
        self.priority_queue = []
        for task in self.tasks:
            heapq.heappush(self.priority_queue, (task['priority'], task['id'], task))

    def undo_last_action(self):
        """Son yapılan işlemi geri al"""
        if not self.undo_stack:
            print("⚠️ Geri alınacak işlem yok")
            return
            
        action, data = self.undo_stack.pop()
        
        if action == 'add':
            # Eklenen görevi sil
            self._remove_task_by_id(data)
            print("↩️ Son ekleme işlemi geri alındı")
            
        elif action == 'complete':
            # Tamamlanma durumunu geri al
            for task in self.tasks:
                if task['id'] == data['id']:
                    task['completed'] = False
                    print(f"↩️ '{task['name']}' görevi tamamlanmamış olarak işaretlendi")
                    break
                    
        elif action == 'delete':
            # Silinen görevi geri ekle
            self.tasks.append(data)
            heapq.heappush(self.priority_queue, (data['priority'], data['id'], data))
            print(f"↩️ '{data['name']}' görevi geri eklendi")

    def _remove_task_by_id(self, task_id):
        """ID'ye göre görev sil"""
        self.tasks = [task for task in self.tasks if task['id'] != task_id]
        self._rebuild_priority_queue()

    def get_next_priority_task(self):
        """Öncelik sırasına göre bir sonraki görevi getir"""
        while self.priority_queue:
            priority, task_id, task = heapq.heappop(self.priority_queue)
            if not task['completed']:
                # Görevi tekrar kuyruğa ekle
                heapq.heappush(self.priority_queue, (priority, task_id, task))
                return task
        
        print("ℹ️ Yapılacak görev bulunamadı")
        return None

    def list_tasks(self, sort_by='priority'):
        """
        Görevleri listele
        :param sort_by: Sıralama kriteri (priority/date/created)
        """
        if not self.tasks:
            print("ℹ️ Görev bulunamadı")
            return
            
        print("\n📝 TO-DO LIST 📝")
        print("-" * 40)
        
        # Sıralama yap
        if sort_by == 'priority':
            sorted_tasks = sorted(self.tasks, key=lambda x: x['priority'])
        elif sort_by == 'date':
            sorted_tasks = sorted(self.tasks, key=lambda x: x['due_date'])
        elif sort_by == 'created':
            sorted_tasks = sorted(self.tasks, key=lambda x: x['created_at'])
        else:
            sorted_tasks = self.tasks
        
        for task in sorted_tasks:
            status = "✓" if task['completed'] else " "
            priority_stars = "★" * task['priority'] + "☆" * (5 - task['priority'])
            print(f"{task['id']}. [{status}] {task['name']}")
            print(f"   Öncelik: {priority_stars} | Son Tarih: {task['due_date']}")
            print(f"   Oluşturulma: {task['created_at'].strftime('%Y-%m-%d %H:%M')}")
            print("-" * 40)

    def search_tasks(self, keyword):
        """
        Görevlerde arama yap
        :param keyword: Aranacak kelime
        """
        found = False
        print(f"\n🔍 '{keyword}' için arama sonuçları:")
        for task in self.tasks:
            if keyword.lower() in task['name'].lower():
                status = "Tamamlandı" if task['completed'] else "Bekliyor"
                print(f"{task['id']}. {task['name']} - Durum: {status}")
                found = True
                
        if not found:
            print("❌ Eşleşen görev bulunamadı")

def main():
    """Ana uygulama döngüsü"""
    todo = ToDoList()
    
    while True:
        print("\n" + "=" * 40)
        print("📋 TO-DO LIST UYGULAMASI")
        print("=" * 40)
        print("1. Yeni Görev Ekle")
        print("2. Görevleri Listele")
        print("3. Görevi Tamamla")
        print("4. Görevi Sil")
        print("5. Son İşlemi Geri Al")
        print("6. Öncelikli Görevi Göster")
        print("7. Görev Ara")
        print("8. Çıkış")
        
        choice = input("Seçiminiz (1-8): ")
        
        try:
            if choice == '1':
                name = input("Görev adı: ")
                priority = int(input("Öncelik (1-5): "))
                due_date = input("Son tarih (YYYY-AA-GG): ")
                todo.add_task(name, priority, due_date if due_date else None)
            
            elif choice == '2':
                sort_by = input("Sıralama (priority/date/created): ")
                todo.list_tasks(sort_by if sort_by in ['priority', 'date', 'created'] else None)
            
            elif choice == '3':
                task_id = int(input("Tamamlanacak görev ID: "))
                todo.complete_task(task_id)
            
            elif choice == '4':
                task_id = int(input("Silinecek görev ID: "))
                todo.delete_task(task_id)
            
            elif choice == '5':
                todo.undo_last_action()
            
            elif choice == '6':
                task = todo.get_next_priority_task()
                if task:
                    print(f"⏭️ Öncelikli görev: {task['name']} (Öncelik: {task['priority']})")
            
            elif choice == '7':
                keyword = input("Aranacak kelime: ")
                todo.search_tasks(keyword)
            
            elif choice == '8':
                print("👋 Çıkılıyor...")
                break
            
            else:
                print("⚠️ Geçersiz seçim!")
        
        except ValueError:
            print("❌ Hatalı giriş! Sayı girmelisiniz")
        except Exception as e:
            print(f"❌ Bir hata oluştu: {str(e)}")

if __name__ == "__main__":
    main()