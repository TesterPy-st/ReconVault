import apiService from '../services/apiService';
import axios from 'axios';

jest.mock('axios');

describe('apiService', () => {
  test('fetchTargets should call GET /api/targets', async () => {
    const data = { targets: [], total: 0 };
    axios.get.mockResolvedValue({ data });
    
    const result = await apiService.getTargets();
    expect(axios.get).toHaveBeenCalledWith(expect.stringContaining('/api/targets'), expect.anything());
    expect(result).toEqual(data);
  });

  test('createTarget should call POST /api/targets', async () => {
    const target = { type: 'domain', value: 'test.com' };
    axios.post.mockResolvedValue({ data: { id: 1, ...target } });
    
    const result = await apiService.createTarget(target);
    expect(axios.post).toHaveBeenCalledWith(expect.stringContaining('/api/targets'), target, expect.anything());
    expect(result.id).toBe(1);
  });
});
