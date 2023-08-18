from metadata.metadata import get_ff_names

class TestFfmpegImagePattern:
    files = [
        {
            'file':'./000001.jpg', 
            'pattern': '%06d.jpg',
            'error': False
        },
        {
            'file':'./GPSD001.jpg', 
            'pattern': 'GPSD%03d.jpg',
            'error': False
        },
        {
            'file':'./MULTISHOT_TEST_VB0001.jpg', 
            'pattern': 'MULTISHOT_TEST_VB%04d.jpg',
            'error': False
        },
        {
            'file':'./MULTISHOT_TEST_VB00001.jpg', 
            'pattern': 'MULTISHOT_TEST_VB%05d.jpg',
            'error': False
        },
        {
            'file':'./MULTISHOT_TEST_000001.JPG', 
            'pattern': 'MULTISHOT_TEST_%06d.JPG',
            'error': False
        },
        {
            'file':'./MULTISHOT_TEST.JPG', 
            'pattern': 'MULTISHOT_TEST.JPG',
            'error': True
        },
    ]
    def test_pattern(self):
        for f in self.files:
            start_num, pattern, err = get_ff_names(f['file'])
            assert err == f['error']
            if err is False:
                print(f['file'], start_num, pattern, f['pattern'])
                assert pattern == f['pattern']
