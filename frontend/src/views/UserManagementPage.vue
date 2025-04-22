                <td class="actions">
                  <button 
                    class="btn btn-action btn-edit" 
                    @click="editUser(user)"
                  >
                    <i class="bi bi-pencil-square"></i>
                    编辑
                  </button>
                  <button 
                    class="btn btn-action btn-delete" 
                    @click="deleteUser(user)"
                  >
                    <i class="bi bi-trash"></i>
                    删除
                  </button>
                </td> 