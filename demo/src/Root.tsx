import { useNavigate } from 'react-router-dom';

const youtubeDomains = [
  'youtube.com',
  'www.youtube.com',
  'youtube.com',
  'youtu.be',
];

const Root = () => {
  const navigate = useNavigate();
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const target = e.currentTarget.getElementsByTagName("input")[0].value;
    for (const domain of youtubeDomains) {
      if (target.startsWith(domain) || target.startsWith('https://' + domain)){
        const url = new URL(target);
        const searchParams = url.searchParams;
        const v = searchParams.get('v');
        if (v) {
          navigate('/video/' + v);
          return;
        }

        const pathname = url.pathname;
        navigate('/video/' + pathname);
        return;
      }
    }

    navigate('/video/' + target);
  }

  return (
    <form className="flex items-center bg-gray-100 rounded-lg p-2 shadow-sm" onSubmit={handleSubmit}>
      <input 
        type="text" 
        className="flex-grow bg-transparent outline-none text-gray-700 placeholder-gray-400 px-2"
      />
    </form>
  );
}

export default Root;
